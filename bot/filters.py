from aiogram.filters import BaseFilter
from aiogram.types import Message
from config import settings


class IsSuperuser(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user is not None:
            if message.from_user.id == settings.SUPERUSER_TG_ID:
                return True
            else:
                return False
        else:
            return False
