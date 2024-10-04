import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv


class AiogramBot:
    def __init__(self, token: str):
        self.bot = Bot(
            token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()

        # Handler registration
        self.dp.message.register(self.command_start_handler, CommandStart())
        self.dp.message.register(self.echo_handler)

    async def command_start_handler(self, message: Message) -> None:
        """
        This handler receives messages with `/start` command
        """
        await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

    async def echo_handler(self, message: Message) -> None:
        """
        Handler will forward received message back to the sender
        """
        try:
            await message.send_copy(chat_id=message.chat.id)
        except TypeError:
            await message.answer("Nice try!")

    async def start(self):
        await self.dp.start_polling(self.bot)


async def main() -> None:
    load_dotenv()
    TOKEN = getenv("BOT_TOKEN")
    bot = AiogramBot(token=TOKEN)
    await bot.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
