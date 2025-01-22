from unittest.mock import AsyncMock

import pytest

from bot.handlers.utils import ping_handler


@pytest.mark.asyncio
async def test_ping_handler():
    text_mock = "/ping"
    message_mock = AsyncMock(text=text_mock)
    await ping_handler(message=message_mock)
    message_mock.reply.assert_called_with("pong!")
