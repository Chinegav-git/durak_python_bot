# -*- coding: utf-8 -*-
"""
Определение фабрики CallbackData для игровых действий.
Это обеспечивает структурированный способ обработки данных
от inline-кнопок, связанных с игровым процессом.

Definition of the CallbackData factory for game actions.
This provides a structured way to handle data from
inline buttons related to gameplay.
"""

from aiogram.filters.callback_data import CallbackData

class GameCallback(CallbackData, prefix="game"):
    """
    Фабрика для создания данных обратного вызова в игре.

    Атрибуты:
    - action (str): Указывает на действие, которое нужно выполнить
                   (например, 'join', 'start', 'take', 'pass').
    - game_id (str, optional): ID игры, к которой относится действие.

    Factory for creating callback data in the game.

    Attributes:
    - action (str): Indicates the action to be performed
                   (e.g., 'join', 'start', 'take', 'pass').
    - game_id (str, optional): The ID of the game to which the action belongs.
    """
    action: str
    game_id: str | None = None
