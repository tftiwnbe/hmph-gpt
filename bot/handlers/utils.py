from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

router = Router()


@router.message(F.text == "/ping")
async def ping_handler(message: types.Message):
    await message.reply("pong!")


@router.message(F.text == "/canacel")
async def canacel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.reply("State cleared!")
