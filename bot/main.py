import asyncio

import redis.asyncio as async_redis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from config import settings
from database import run_async_upgrade, sessionmanager
from loguru import logger
from utils.logging import logging_setup

redis = async_redis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0")
token = settings.BOT_TOKEN.get_secret_value()
storage = RedisStorage(redis)
bot = Bot(
    token,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)
dispatcher = Dispatcher(storage=storage)


async def main():
    logger.info("⚡️ Powering up...")

    # Updating database
    await run_async_upgrade()

    try:
        from handlers import superuser, users, utils

        dispatcher.include_routers(
            utils.router,
            superuser.router,
            users.router,
        )
        await dispatcher.start_polling(bot, handle_signals=False)
    except Exception as e:
        logger.critical(e)
    finally:
        await bot.session.close()

        # Close the Redis connection and any DB sessions
        await redis.aclose()
        if sessionmanager._engine is not None:
            await sessionmanager.close()


async def shutdown():
    logger.warning("⚡️ Powering off... ")


if __name__ == "__main__":
    logging_setup()
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        loop.run_until_complete(shutdown())
        loop.close()
        logger.success("System has safely shut down. See you soon! ✨\n")
