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
# ИМПОРТ: Добавлена система локализации.
from durak.utils.i18n import t

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
    - Жестко закодированная строка заменена на ключ локализации.

    Handles the legacy commands /stats, /on_stats, /off_stats.
    Informs the user that this functionality has been moved to the /settings menu.

    FIXED:
    - The message text has been translated into Russian.
    - Comprehensive docstrings have been added for the module and the function.
    - The hardcoded /settings command has been replaced with an import.
    - The hardcoded string has been replaced with a localization key.
    """
    # ИСПРАВЛЕНО: Текст заменен на ключ из системы локализации.
    # FIXED: The text has been replaced with a key from the localization system.
    await message.answer(t(
        'settings.stats_control',
        command=Commands.SETTINGS
    ))
