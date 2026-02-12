from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from config import Config

class IsAdminFilter(BoundFilter):
    """
    Custom filter to check if the user is a bot admin.
    """
    key = 'is_admin'

    async def check(self, message: types.Message) -> bool:
        return message.from_user.id in Config.ADMINS
