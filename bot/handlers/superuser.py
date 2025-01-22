from aiogram import Router, types
from database import get_db_session
from database.crud.user import update_user
from database.schemas.user import UserUpdate
from loguru import logger

from main import bot
from keyboards.users import UsersCallbackFactory

router = Router()


async def get_decision_text(callback_data: UsersCallbackFactory) -> str:
    return "Approved" if callback_data.status else "Rejected"


async def get_user_answer(callback_data: UsersCallbackFactory) -> str:
    return (
        "Your account has been activated. Welcome aboard!"
        if callback_data.status
        else "Unfortunately, your access request was not approved. If you have any questions, please contact support."
    )


@router.callback_query(UsersCallbackFactory.filter())
async def user_status_callback_handler(
    callback: types.CallbackQuery, callback_data: UsersCallbackFactory
) -> None:
    async for session in get_db_session():
        user_data = UserUpdate(
            tg_user_id=callback_data.user_id, is_active=callback_data.status
        )
        await update_user(session, user_data)

    decision_text = await get_decision_text(callback_data)

    if callback.message is not None:
        callback_answer = f"{callback.message.text.replace(' Please choose an action:', '..\n')}`{decision_text}`"  # type: ignore
        await callback.message.edit_text(callback_answer)  # type: ignore
    else:
        logger.error("Callback message is None")

    user_answer = await get_user_answer(callback_data)
    await bot.send_message(chat_id=callback_data.user_id, text=user_answer)
    await callback.answer()
