from aiogram.filters import Filter
from aiogram.types import Message
from app.core.security import is_admin


class AdminFilter(Filter):
    key = "is_admin"

    async def __call__(self, message: Message) -> bool:
        return is_admin(message.from_user.id)
