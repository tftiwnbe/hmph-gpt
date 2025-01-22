from typing import Optional

from loguru import logger
from sqlalchemy import String, or_, select
from sqlalchemy.exc import DataError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import UserModel
from ..schemas.user import UserCreate, UserSearch, UserUpdate


class UserAlreadyExistsError(Exception):
    def __init__(self, user):
        self.user = user
        self.message = f"User with ID {self.user.tg_user_id} already exists"
        logger.info(self.message)
        super().__init__(self.message)


class FieldLengthError(ValueError):
    def __init__(self, field_name: str, max_length: int, actual_length: int):
        self.field_name = field_name
        self.max_length = max_length
        self.actual_length = actual_length
        self.message = f"Value for '{field_name}' exceeds max length of {max_length} characters. Actual length: {actual_length}."
        logger.info(self.message)
        super().__init__(self.message)


class UserNotFoundError(Exception):
    def __init__(self, username=None, tg_user_id=None, ds_user_id=None, **kwargs):
        self.tg_user_id = tg_user_id
        self.ds_user_id = ds_user_id
        self.username = username
        self.message = (
            f"User not found ({self.username} - {self.tg_user_id} - {self.ds_user_id})"
        )
        logger.info(self.message)
        super().__init__(self.message)


async def add_user(session: AsyncSession, user_data: UserCreate) -> None:
    """Register user with tg_user_id or ds_user_id"""
    logger.info("Registering user...")

    user_id_type = (
        f"TG_ID={user_data.tg_user_id}"
        if user_data.tg_user_id
        else f"DS_ID={user_data.ds_user_id}"
    )

    existing_user = await session.scalar(
        select(UserModel).where(UserModel.tg_user_id == user_data.tg_user_id)
    )
    if existing_user:
        raise UserAlreadyExistsError(existing_user)

    new_user = UserModel(**user_data.dict())

    session.add(new_user)
    try:
        await session.commit()
        logger.success(f"User {user_data.username} registered with {user_id_type}")
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Error adding user {user_data.username} ({user_id_type}): {e}")
        raise


async def update_user(session: AsyncSession, user_data: UserUpdate) -> None:
    """Update user data for a user with either tg_user_id or ds_user_id, enforcing field length constraints."""
    logger.info("Updating user...")

    query = select(UserModel)
    if user_data.tg_user_id is not None:
        query = query.where(UserModel.tg_user_id == user_data.tg_user_id)
    elif user_data.ds_user_id is not None:
        query = query.where(UserModel.ds_user_id == user_data.ds_user_id)
    else:
        raise ValueError("Either tg_user_id or ds_user_id must be provided.")

    user = await session.scalar(query)
    if user is None:
        raise UserNotFoundError(**user_data.dict(exclude_unset=True))

    if user_data.username:
        username_exists = await session.scalar(
            select(UserModel)
            .where(UserModel.username == user_data.username)
            .where(UserModel.id != user.id)
        )
        if username_exists:
            logger.info("Choosen alredy registered username")
            raise ValueError(f'The username "{user_data.username}" is already taken.')

    for key, value in user_data.dict(exclude_unset=True).items():
        if value is not None:
            column = getattr(UserModel, key, None)

            if column is not None and isinstance(column.type, String):
                max_length = column.type.length
                if max_length and isinstance(value, str) and len(value) > max_length:
                    raise FieldLengthError(
                        field_name=key, max_length=max_length, actual_length=len(value)
                    )

            setattr(user, key, value)

    try:
        await session.commit()
        logger.success(
            f"User {user_data.tg_user_id or user_data.ds_user_id} updated (user_id={user.id})"
        )
    except DataError as e:
        await session.rollback()
        logger.error(
            f"Data error updating user {user_data.tg_user_id or user_data.ds_user_id}=(user_id {user.id}): {e}"
        )
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(
            f"Error updating user {user_data.tg_user_id or user_data.ds_user_id} (user_id {user.id}): {e}"
        )
        raise


async def get_user(
    session: AsyncSession, user_search: UserSearch
) -> Optional[UserModel]:
    """Search for a user by tg_user_id, ds_user_id, or user_name. Optionally create a user if not found."""
    logger.info("Searching user...")
    try:
        conditions = []
        if user_search.tg_user_id:
            conditions.append(UserModel.tg_user_id == user_search.tg_user_id)
        if user_search.ds_user_id:
            conditions.append(UserModel.ds_user_id == user_search.ds_user_id)
        if user_search.username:
            conditions.append(UserModel.username == user_search.username)

        if not conditions:
            raise ValueError(
                "At least one search parameter (tg_user_id, ds_user_id, user_name) must be provided"
            )

        result = await session.execute(select(UserModel).where(or_(*conditions)))
        user = result.scalar_one_or_none()

        if not user:
            logger.warning("User with provided search criteria not found")
            if user_search.create:
                logger.info("Creating new user...")
                new_user = UserModel(
                    tg_user_id=user_search.tg_user_id,
                    ds_user_id=user_search.ds_user_id,
                    user_name=user_search.username
                    or f"User_{user_search.tg_user_id or user_search.ds_user_id}",
                )
                session.add(new_user)
                await session.commit()
                logger.success(
                    f"User registered with provided criteria: {user_search.dict(exclude={'create'})}"
                )
                return new_user
            else:
                raise UserNotFoundError(**user_search.dict(exclude={"create"}))

        logger.info("User found successfully")
        return user

    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Error retrieving or creating user: {e}")
        raise
