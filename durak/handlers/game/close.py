# -*- coding: utf-8 -*-
"""
Модуль для обработки закрытия лобби игры.

ВАЖНО: Логика этого модуля временно отключена и требует доработки.

Module for handling the closing of a game lobby.

IMPORTANT: The logic in this module is temporarily disabled and requires further development.
"""

from aiogram import F, Router, types

# ИСПРАВЛЕНО: Корректный импорт GameCallback и GameManager
# FIXED: Correct import for GameCallback and GameManager
from durak.logic.game_manager import GameManager
from .game_callback import GameCallback

router = Router()


@router.callback_query(GameCallback.filter(F.action == "close"))
async def close_lobby_handler(
    query: types.CallbackQuery, callback_data: GameCallback, gm: GameManager
):
    """
    Обрабатывает закрытие лобби. Только создатель игры может это сделать.
    
    Handles closing the lobby. Only the game creator can perform this action.
    """
    # TODO: Реализовать полноценную логику закрытия лобби.
    # Текущий код закомментирован, так как он содержит критические ошибки
    # и выполняет неверное действие (завершает игру вместо закрытия лобби).
    #
    # ПРОБЛЕМЫ:
    # 1. НЕВЕРНОЕ ДЕЙСТВИЕ: Вызывается `gm.end_game(game)`, что полностью
    #    завершает игру. Требуется новый метод в GameManager, например, `gm.close_lobby(game)`,
    #    который бы просто менял флаг в объекте игры.
    # 2. НЕВЕРНОЕ ПОЛУЧЕНИЕ ИГРЫ: Используется `gm.get_game_from_chat(game_id)`,
    #    что неверно. Нужно использовать `gm.get_game(int(game_id))`.
    # 3. ОТСУТСТВИЕ КНОПКИ: В интерфейсе лобби нет кнопки, вызывающей этот обработчик.
    #
    # ПЛАН РЕАЛИЗАЦИИ:
    # 1. Добавить в `game.py` (объект игры) поле типа `lobby_is_closed: bool`.
    # 2. Добавить в `game_manager.py` метод `async def close_lobby(game)`.
    # 3. Раскомментировать и переписать этот обработчик для вызова `close_lobby`.
    # 4. Добавить кнопку "Закрыть лобби" в `new.py` и `join.py`.
    # 5. В `join.py` (в `process_join`) добавить проверку на закрытое лобби.
    
    await query.answer("Функция 'Закрыть лобби' находится в разработке.", show_alert=True)
