# -*- coding: utf-8 -*-
"""
Этот модуль содержит фильтры, связанные с состоянием игры.

This module contains filters related to the game state.
"""

from aiogram.filters import Filter
from aiogram.types import Message

from durak.logic.game_manager import GameManager
from durak.objects import GameNotFoundError


class InGameFilter(Filter):
    """
    Фильтр, который проверяет, находится ли пользователь в активной игре.
    Это позволяет отделить обработку игровых действий от обычных команд.

    A filter that checks if a user is in an active game.
    This helps separate the processing of game actions from regular commands.
    """
    async def __call__(self, message: Message, gm: GameManager) -> bool:
        """
        Выполняет проверку.

        :param message: Объект сообщения.
        :param gm: Менеджер игр.
        :return: True, если пользователь в игре, иначе False.
        """
        if not message.from_user:
            return False
        
        try:
            game = await gm.get_game_by_user_id(message.from_user.id)
            # Фильтр сработает, только если игра существует и уже началась.
            # The filter will only trigger if the game exists and has started.
            return game is not None and game.started
        except GameNotFoundError:
            # Если игра не найдена, это не игровое действие.
            # If the game is not found, it is not a game action.
            return False
