# -*- coding: utf-8 -*-
"""
Этот файл является точкой входа для пакета обработчиков.
Он агрегирует все роутеры из дочерних модулей и подпакетов в один главный роутер.

This file is the entry point for the handlers package.
It aggregates all routers from child modules and subpackages into a single main router.
"""

from aiogram import Router


def setup(game_manager=None) -> Router:
    """
    Настраивает и возвращает главный роутер для всех обработчиков.

    Эта функция импортирует и инициализирует роутеры из всех подмодулей
    (например, `game`, `info`, `settings` и т.д.) и объединяет их
    в один `Router`.

    Sets up and returns the main router for all handlers.

    This function imports and initializes routers from all submodules
    (e.g., `game`, `info`, `settings`, etc.) and combines them
    into a single `Router`.
    """
    # Ленивый импорт для предотвращения циклических зависимостей
    # Lazy import to prevent circular dependencies
    from . import (
        card_theme,
        game_mode,
        settings,
    )
    from .game import setup as setup_game
    from .info import setup as setup_info
    from . import inline

    # Создание экземпляра главного роутера
    # Create an instance of the main router
    router_instance = Router()

    # Настройка и получение роутеров из подпакетов
    # Setup and get routers from subpackages
    game_router = setup_game(game_manager)
    info_router = setup_info()

    # Включение роутеров из подпакетов в главный роутер
    # Include routers from subpackages into the main router
    router_instance.include_router(game_router)
    router_instance.include_router(info_router)
    router_instance.include_router(inline.router)

    # Включение роутеров из отдельных модулей
    # Include routers from individual modules
    for module in (
        card_theme,
        game_mode,
        settings,
    ):
        router_instance.include_router(module.router)

    return router_instance
