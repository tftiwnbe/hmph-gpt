from aiogram.filters import BaseFilter
from aiogram.types import Message
from config import settings
from database import get_db_session
from database.crud.user import UserNotFoundError, get_user
from database.schemas.user import UserSearch
from loguru import logger


class IsSuperuser(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user is not None:
            if message.from_user.id == settings.SUPERUSER_TG_ID:
                return True
            else:
                return False
        else:
            return False


class IsActiveUser(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user is None:
            return False

        user_data = UserSearch(tg_user_id=message.from_user.id)

        try:
            async for session in get_db_session():
                user = await get_user(session, user_data)
                return bool(user and user.is_active)
        except UserNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False

        return False
