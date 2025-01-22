import sys
import logging
from loguru import logger
from config import settings


# https://loguru.readthedocs.io/en/stable/overview.html
class InterceptHandler(logging.Handler):
    LEVELS_MAP = {
        logging.CRITICAL: "CRITICAL",
        logging.ERROR: "ERROR",
        logging.WARNING: "WARNING",
        logging.INFO: "INFO",
        logging.DEBUG: "DEBUG",
    }

    def _get_level(self, record):
        return self.LEVELS_MAP.get(record.levelno, record.levelno)

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame is not None:
            if (  # remove for more compact logs
                "logging" not in frame.f_code.co_filename
                and "loguru" not in frame.f_code.co_filename
            ):
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def logging_setup():
    logger.configure(
        handlers=[  # type: ignore
            # std logs
            dict(
                sink=sys.stderr,
                level=settings.LOG_LEVEL,
                format="|<level>{level}</level>| <i>{name}</i> - <level>{message}</level>",
                colorize=True,
                backtrace=settings.DEVELOPMENT,
                diagnose=settings.DEVELOPMENT,
                catch=settings.DEVELOPMENT,
            ),
            # info logs
            dict(
                sink="../data/logs/info.log",
                level="INFO",
                format="{message}",
                rotation="1 week",
                compression="zip",
                enqueue=True,
                serialize=True,
            ),
            # events logs
            dict(
                sink="../data/logs/events.log",
                level="SUCCESS",
                format="{message}",
                rotation="1 week",
                compression="zip",
                enqueue=True,
                serialize=True,
            ),
        ],
    )
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)
    logger.disable("sqlalchemy.engine.base")
