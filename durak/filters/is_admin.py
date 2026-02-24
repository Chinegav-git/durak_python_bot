from aiogram import types
from aiogram.filters import Filter
from typing import Union

from config import Config

class IsAdminFilter(Filter):
    """
    Перевіряє, чи є користувач глобальним адміном БОТА (з конфігу).
    """
    def __init__(self, is_admin: bool) -> None:
        self.is_admin = is_admin

    async def __call__(self, message: Union[types.Message, types.CallbackQuery]) -> bool:
        user_id = message.from_user.id
        return (user_id in Config.ADMINS) == self.is_admin
