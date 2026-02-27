# -*- coding: utf-8 -*-
"""
Вспомогательные утилиты и функции-предикаты.

Этот модуль предоставляет набор простых функций, которые используются для проверки
прав доступа пользователя к определенным действиям в игре или в боте.
Они инкапсулируют логику проверки, является ли пользователь создателем игры,
администратором чата или глобальным администратором бота.

-------------------------------------------------------------------------------------

Auxiliary utilities and predicate functions.

This module provides a set of simple functions used to check a user's access
rights for specific actions in the game or the bot.
They encapsulate the logic for checking if a user is the game creator,
a chat administrator, or a global bot administrator.
"""

from aiogram import Bot
from aiogram.types import Chat

from config import Config
from ..objects import Game


def user_is_creator(user_id: int, game: Game) -> bool:
    """Проверяет, является ли пользователь создателем игры.
    
    Checks if a user is the creator of the game.
    """
    return user_id == game.creator_id


def user_is_bot_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь глобальным администратором бота.
    
    Checks if a user is a global bot admin.
    """
    return user_id in Config.ADMINS


async def get_admin_ids(bot: Bot, chat_id: int) -> list[int]:
    """Возвращает список ID администраторов для указанного чата.
    Если это личный чат (chat_id > 0), возвращает пустой список.
    
    Returns a list of admin IDs for a given chat.
    If it's a private chat (chat_id > 0), returns an empty list.
    """
    if chat_id > 0:
        return []
        
    chat_admins = await bot.get_chat_administrators(chat_id)
    return [admin.user.id for admin in chat_admins]


async def user_is_chat_admin(bot: Bot, user_id: int, chat_id: int) -> bool:
    """Проверяет, является ли пользователь администратором в конкретном чате.
    В личном чате всегда возвращает True.
    
    Checks if a user is an admin in a specific chat.
    Always returns True in a private chat.
    """
    if chat_id > 0:
        return True
        
    return user_id in await get_admin_ids(bot, chat_id)


async def user_is_creator_or_admin(bot: Bot, user_id: int, game: Game, chat_id: int) -> bool:
    """
    Проверяет, является ли пользователь создателем игры или администратором чата.
    
    Checks if a user is the game creator or a chat administrator.
    """
    return user_is_creator(user_id, game) or await user_is_chat_admin(bot, user_id, chat_id)


async def user_can_kick(bot: Bot, user_id: int, chat: Chat, game: Game) -> bool:
    """
    Проверяет, может ли пользователь исключить другого игрока.
    Может создатель игры, администратор чата или администратор бота.
    
    Checks if a user can kick another player.
    Allowed for the game creator, chat admin, or bot admin.
    """
    return (
        user_is_creator(user_id, game) or
        user_is_bot_admin(user_id) or
        await user_is_chat_admin(bot, user_id, chat.id)
    )


async def user_can_change_settings(bot: Bot, user_id: int, chat_id: int) -> bool:
    """
    Проверяет, может ли пользователь изменять настройки игры (тему, режим).
    Может администратор чата или администратор бота.
    
    Checks if a user can change game settings (theme, mode).
    Allowed for a chat admin or bot admin.
    """
    return user_is_bot_admin(user_id) or await user_is_chat_admin(bot, user_id, chat_id)