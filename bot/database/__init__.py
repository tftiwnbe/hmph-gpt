import contextlib
import time
from typing import Any, AsyncIterator

from alembic import command, config
from config import settings
from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
    __mapper_args__ = {"eager_defaults": True}


# Heavily inspired by https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, bind=self._engine, expire_on_commit=False
        )

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)

sessionmanager = DatabaseSessionManager(DATABASE_URL, {"echo": settings.ECHO_SQL})


async def get_db_session():
    async with sessionmanager.session() as session:
        yield session


def run_upgrade(connection, cfg) -> None:
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


async def run_async_upgrade(alembic_cfg_path: str = "migrations/alembic.ini") -> None:
    logger.info("Running migrations...")
    start_time = time.monotonic()
    try:
        async with sessionmanager.connect() as connection:
            await connection.run_sync(
                lambda conn: run_upgrade(conn, config.Config(alembic_cfg_path))
            )
        elapsed_time = time.monotonic() - start_time
        logger.success(f"Database up to date in {elapsed_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
