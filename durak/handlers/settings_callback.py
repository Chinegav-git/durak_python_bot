# -*- coding: utf-8 -*-
"""
Определение фабрики CallbackData для меню настроек.
Это обеспечивает структурированный и безопасный способ
обработки данных обратного вызова от inline-кнопок.
Definition of the CallbackData factory for the settings menu.
This provides a structured and safe way to handle
callback data from inline buttons.
"""

from aiogram.filters.callback_data import CallbackData

class SettingsCallback(CallbackData, prefix="settings"):
    """
    Фабрика для создания данных обратного вызова в настройках.

    Атрибуты:
    - level (str): Указывает на текущий уровень в меню настроек 
                   (например, 'main_menu', 'gamemode', 'card_theme').
    - value (str, optional): Хранит дополнительное значение, 
                             например, ID выбранной темы или режима.

    Factory for creating callback data in settings.

    Attributes:
    - level (str): Indicates the current level in the settings menu
                   (e.g., 'main_menu', 'gamemode', 'card_theme').
    - value (str, optional): Stores an additional value,
                             e.g., the ID of the selected theme or mode.
    """
    level: str
    value: str | None = None
