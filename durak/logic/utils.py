from ..objects import Game
from aiogram.types import User
from aiogram import Bot
from config import Config


def user_is_creator(user_id: int, game: Game):
    return user_id == game.creator_id


def user_is_bot_admin(user_id: int):
    return user_id in Config.ADMINS


async def user_is_admin(user_id: int, chat_id: int):
    return user_id in (await get_admin_ids(chat_id))


async def user_is_creator_or_admin(user_id: int, game: Game):
    return user_is_creator(user_id, game) or user_is_bot_admin(user_id) or (await user_is_admin(user_id, game.chat_id))


async def user_can_change_gamemode(user_id: int, chat_id: int):
    """Checks if a user can change the game mode (bot admin or chat admin)."""
    return user_is_bot_admin(user_id) or (await user_is_admin(user_id, chat_id))


async def get_admin_ids(chat_id: int):
    """Returns a list of admin IDs for a given chat."""
    bot = Bot.get_current()
    chat_admins = await bot.get_chat_administrators(chat_id)
    return [admin.user.id for admin in chat_admins]
