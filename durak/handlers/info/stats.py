# -*- coding: utf-8 -*-
"""
Модуль для обработки устаревших команд статистики.
Сообщает пользователю, что управление статистикой перенесено в меню настроек.

Module for handling legacy statistics commands.
Informs the user that statistics management has been moved to the settings menu.
"""

from aiogram import Router, types
from aiogram.filters import Command

# ИМПОРТ: Команды импортируются из единого источника для консистентности.
from config import Commands

router = Router()

@router.message(Command(Commands.STATS, Commands.OFF_STATS, Commands.ON_STATS))
async def stats_redirect_handler(message: types.Message):
    """
    Обрабатывает устаревшие команды /stats, /on_stats, /off_stats.
    Сообщает пользователю, что эта функция была перенесена в меню /settings.
    
    ИСПРАВЛЕНО:
    - Текст сообщения переведен на русский язык.
    - Добавлены полные docstring для модуля и функции.
    - Жестко закодированная команда /settings заменена на импорт.

    Handles the legacy commands /stats, /on_stats, /off_stats.
    Informs the user that this functionality has been moved to the /settings menu.

    FIXED:
    - The message text has been translated into Russian.
    - Comprehensive docstrings have been added for the module and the function.
    - The hardcoded /settings command has been replaced with an import.
    """
    # ИСПРАВЛЕНО: Текст переведен и исправлен.
    await message.answer(
        "📊 Управление статистикой было перенесено в единое меню настроек.\n\n"
        f"👉 Пожалуйста, воспользуйтесь командой /{Commands.SETTINGS}, чтобы посмотреть или изменить свои настройки."
    )
