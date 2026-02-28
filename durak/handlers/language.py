# -*- coding: utf-8 -*-
"""
Модуль для генерации клавиатуры выбора языка.
Module for generating the language selection keyboard.
"""

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from durak.utils.i18n import t, i18n
from durak.handlers.settings_callback import SettingsCallback


def get_language_keyboard(current_language: str) -> types.InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора языка.
    
    ИСПРАВЛЕНО:
    - Удалены все обработчики команд и callback-ов, так как эта логика
      теперь централизована в durak/handlers/settings.py.
    - Модуль теперь отвечает только за отрисовку клавиатуры.
    - Исправлен некорректный текст в `call.answer` (логика удалена).
    
    Creates the language selection keyboard.
    
    FIXED:
    - Removed all command and callback handlers, as this logic is now
      centralized in durak/handlers/settings.py.
    - The module is now responsible only for rendering the keyboard.
    - Corrected incorrect text in `call.answer` (logic removed).
    """
    builder = InlineKeyboardBuilder()
    
    languages = i18n.get_available_languages()
    
    for lang_code, lang_name in languages.items():
        is_current = lang_code == current_language
        text = f"🌐 {lang_name} {'✅' if is_current else ''}"
        builder.button(
            text=text,
            callback_data=SettingsCallback(level="set_language", value=lang_code).pack()
        )
    
    builder.adjust(1)
    
    # Кнопка "Назад"
    # Back button
    builder.button(
        text=t("buttons.back"),
        callback_data=SettingsCallback(level="main_menu").pack()
    )
    builder.adjust(1)
    
    return builder.as_markup()
