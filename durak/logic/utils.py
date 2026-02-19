from aiogram import Bot
from aiogram.types import Chat
from ..objects import Game
from config import Config

def user_is_creator(user_id: int, game: Game):
    """Checks if a user is the creator of the game."""
    return user_id == game.creator_id

def user_is_bot_admin(user_id: int):
    """Checks if a user is a global bot admin."""
    return user_id in Config.ADMINS

async def get_admin_ids(bot: Bot, chat_id: int) -> list[int]:
    """Returns a list of admin IDs for a given chat."""
    chat_admins = await bot.get_chat_administrators(chat_id)
    return [admin.user.id for admin in chat_admins]

async def user_is_chat_admin(bot: Bot, user_id: int, chat_id: int) -> bool:
    """Checks if a user is an admin in a specific chat."""
    return user_id in await get_admin_ids(bot, chat_id)

async def user_is_creator_or_admin(bot: Bot, user_id: int, game: Game, chat: Chat) -> bool:
    """
    Checks if a user is the game creator, a bot admin, or a chat admin.
    """
    return (
        user_is_creator(user_id, game) or
        user_is_bot_admin(user_id) or
        await user_is_chat_admin(bot, user_id, chat.id)
    )

async def user_can_change_gamemode(bot: Bot, user_id: int, chat_id: int) -> bool:
    """Checks if a user can change the game mode (bot admin or chat admin)."""
    return user_is_bot_admin(user_id) or await user_is_chat_admin(bot, user_id, chat_id)
