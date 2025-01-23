import re

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from config import settings
from database import get_db_session
from database.crud.user import (
    FieldLengthError,
    UserAlreadyExistsError,
    UserNotFoundError,
    add_user,
    update_user,
)
from database.schemas.user import UserCreate, UserUpdate
from handlers.gpt import generate_response
from keyboards.users import get_name_keyboard, get_status_keyboard
from loguru import logger
from main import bot
from states import UserState

router = Router()


@router.message(StateFilter(None), Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    if message.from_user is None:
        await message.answer("Something went wrong. Please try again later.")
        return

    username = message.from_user.username or f"user_{message.from_user.id}"
    keyboard = await get_name_keyboard(username)

    try:
        async for session in get_db_session():
            user_data = UserCreate(username=username, tg_user_id=message.from_user.id)
            await add_user(session, user_data)
            await message.answer(
                'Hey there! Great to meet you! Could you share your name so I don’t have to call you "`Mystery Guest`"?',
                reply_markup=keyboard,
            )
            await state.set_state(UserState.waiting_username)
    except UserAlreadyExistsError as e:
        await message.answer(
            f"Welcome back, {e.user.username}. Glad to see you're back!"
        )
    except Exception as e:
        await message.reply(
            f"An unexpected error occurred: {e}",
            parse_mode=ParseMode.HTML,
        )


@router.message(StateFilter(UserState.waiting_username), F.text)
async def catching_username_handler(message: types.Message, state: FSMContext):
    if message.from_user is None or message.text is None:
        await message.reply("Something went wrong. Please try again.")
        return

    keyboard = await get_name_keyboard()

    match = re.search(r"[^a-zA-Z0-9_ ]", message.text)
    if match:
        invalid_char = match.group(0)
        await message.answer(
            f"Oops! It looks like your username starts with an invalid character: `{invalid_char}`. Please provide your name again using only letters and numbers.",
            reply_markup=keyboard,
        )
        return
    try:
        async for session in get_db_session():
            user_data = UserUpdate(
                username=message.text, tg_user_id=message.from_user.id
            )
            await update_user(session, user_data)
            await message.answer(
                f"Got it, `{message.text}`! Nice to meet you 😊",
                reply_markup=types.ReplyKeyboardRemove(),
            )
            await state.clear()
            await message.answer(
                "Thanks for joining us. Your account is pending activation by an administrator. We'll notify you once it's ready for use."
            )
            keyboard = await get_status_keyboard(message.from_user.id)
            superuser_id = settings.SUPERUSER_TG_ID
            forwarded = await message.forward(superuser_id)
            await bot.send_message(
                superuser_id,
                f"User `{message.from_user.username}` (TGID: `{message.from_user.id}`) has requested access. Please choose an action:",
                reply_markup=keyboard,
                reply_to_message_id=forwarded.message_id,
            )

    except UserNotFoundError as e:
        await message.reply(
            f"Error occurred while updating username: {e}",
            parse_mode=ParseMode.HTML,
        )
    except FieldLengthError:
        await message.answer(
            "Oops! Your username seems a bit too long. Could you please provide a shorter name?",
            reply_markup=keyboard,
        )
    except ValueError:
        await message.answer(
            "It looks like that username is already taken. Could you try a different one?",
            reply_markup=keyboard,
        )
    except Exception as e:
        await message.reply(
            f"An unexpected error occurred: {e}",
            parse_mode=ParseMode.HTML,
        )
        logger.error(e)


@router.message(StateFilter(None), F.text)
async def ask_gpt(message: types.Message):
    if message.text is not None:
        answer = "Failed to retrieve a response."
        used_model = ""
        completion_tokens = 0
        prompt_tokens = 0

        try:
            (
                answer,
                used_model,
                completion_tokens,
                prompt_tokens,
            ) = await generate_response(message.text)
        except Exception as e:
            answer = f"An error occurred while processing the request: {str(e)}"

        if answer is None:
            answer = "GPT did not return a response."

        await message.answer(answer)
    else:
        await message.answer("The message does not contain any text.")
