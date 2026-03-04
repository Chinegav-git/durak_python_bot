# -*- coding: utf-8 -*-
"""
Этот пакет содержит все обработчики, связанные с игровым процессом.

- Создание и управление лобби (`new`, `join`, `leave`, `kick`, `start`).
- Обработка действий во время игры (`actions`).
- Административные команды (`kill`, `close`).
- Автоматические действия (`auto_leave`).

This package contains all handlers related to the gameplay.

- Creating and managing the lobby (`new`, `join`, `leave`, `kick`, `start`).
- Handling in-game actions (`actions`).
- Administrative commands (`kill`, `close`).
- Automatic actions (`auto_leave`).
"""

from aiogram import Router

def setup(game_manager=None) -> Router:
    """
    Настраивает и возвращает главный роутер для всех игровых обработчиков.

    Эта функция импортирует и объединяет роутеры из всех модулей
    внутри пакета `game`.
    
    ИСПРАВЛЕНО: Добавлены docstring'и для модуля и функции.
    ИСПРАВЛЕНО: `actions` перемещен в конец для правильного порядка регистрации обработчиков.

    Sets up and returns the main router for all game handlers.

    This function imports and combines the routers from all modules
    within the `game` package.

    FIXED: Added docstrings for the module and the function.
    FIXED: `actions` moved to the end for correct handler registration order.
    """
    # Ленивый импорт для предотвращения циклических зависимостей
    # Lazy import to prevent circular dependencies
    from . import (
        actions,
        auto_leave,
        close,
        global_leave,
        join,
        kick,
        kill,
        leave,
        lobby_kick,
        new,
        start,
        test_win,
        process_chosen,
    )

    router = Router()

    # Ініціалізуємо gm у всіх модулях, які його потребують
    # Initialize gm in all modules that need it
    if game_manager:
        kill.gm = game_manager
        lobby_kick.gm = game_manager
        test_win.gm = game_manager

    # Регистрация всех игровых роутеров.
    # ПОРЯДОК ВАЖЕН: сначала специфичные команды, потом общие текстовые обработчики.
    # Register all game routers.
    # ORDER IS IMPORTANT: specific commands first, then generic text handlers.
    for module in (
        auto_leave,
        close,
        global_leave,
        join,
        kick,
        kill,
        leave,
        lobby_kick,
        new,
        start,
        test_win,
        process_chosen,
        # `actions` должен быть последним, чтобы не перехватывать команды
        # `actions` must be last to avoid intercepting commands
        actions,
    ):
        router.include_router(module.router)

    return router
