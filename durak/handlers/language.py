# -*- coding: utf-8 -*-
"""
Language selection handlers.
Обробники вибору мови.
"""

from aiogram import types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from durak.utils.i18n import t, set_language, i18n
from durak.utils.language_detector import language_manager
from durak.handlers.settings_callback import SettingsCallback


def get_language_keyboard(current_language: str) -> types.InlineKeyboardMarkup:
    """Create language selection keyboard."""
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
    
    # Back button
    builder.button(
        text=t("buttons.back"),
        callback_data=SettingsCallback(level="main_menu").pack()
    )
    builder.adjust(1)
    
    return builder.as_markup()


async def handle_language_command(message: types.Message):
    """Handle /language command."""
    # Get current user language
    current_language = await language_manager.get_or_detect_language(message.from_user)
    set_language(current_language)
    
    await message.answer(
        "🌐 **Мова / Language**\n\n"
        "Оберіть мову інтерфейсу:\n"
        "Choose your interface language:",
        reply_markup=get_language_keyboard(current_language)
    )


async def handle_language_callback(call: types.CallbackQuery, callback_data: SettingsCallback):
    """Handle language selection callback."""
    lang_code = callback_data.value
    
    # Set user language preference
    await language_manager.set_user_language(call.from_user.id, lang_code)
    set_language(lang_code)
    
    # Update the message
    await call.message.edit_text(
        "🌐 **Мова / Language**\n\n"
        "Оберіть мову інтерфейсу:\n"
        "Choose your interface language:",
        reply_markup=get_language_keyboard(lang_code)
    )
    
    await call.answer(t("settings.theme_already_set"))
