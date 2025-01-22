from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class UsersCallbackFactory(CallbackData, prefix="user"):
    user_id: int
    status: bool


async def get_status_keyboard(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Reject",
        callback_data=UsersCallbackFactory(user_id=user_id, status=False),
    )
    builder.button(
        text="Approve",
        callback_data=UsersCallbackFactory(user_id=user_id, status=True),
    )
    return builder.as_markup()


async def get_name_keyboard(username: str = "Strange Human") -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Mystery Guest"), KeyboardButton(text=username)],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Tell me your name...",
    )
    return keyboard
