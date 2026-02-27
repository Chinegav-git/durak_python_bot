# -*- coding: utf-8 -*-
"""
Этот модуль является центральной точкой входа для меню настроек.
Он отвечает за обработку команды /settings и отображение главного меню,
откуда пользователь может перейти в другие разделы настроек.

This module is the central entry point for the settings menu.
It handles the /settings command and displays the main menu,
from where the user can navigate to other settings sections.
"""

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from durak.db.models import Chat, ChatSetting
from durak.logic import utils
from durak.utils.i18n import t
from durak.utils.language_detector import language_manager
# ИСПРАВЛЕНО: Теперь используется SettingsCallback для навигации по меню.
# FIXED: Now using SettingsCallback for menu navigation.
from .settings_callback import SettingsCallback

router = Router()

async def get_main_settings_keyboard(chat: types.Chat, is_admin: bool, user_id: int = None) -> types.InlineKeyboardMarkup:
    """
    Генерирует главное меню настроек в виде inline-клавиатуры.
    
    ИСПРАВЛЕНО: 
    - Удалена вся логика, связанная с FSM и жестко закодированными значениями.
    - Кнопки теперь используют SettingsCallback для навигации, что позволяет
      делегировать обработку соответствующим модулям (game_mode.py, card_theme.py).
    - Весь текст переведен на русский язык для единообразия.
    - Использование pony.orm заменено на асинхронные вызовы Tortoise ORM.
    - Добавлена кнопка выбора языка.

    Generates the main settings menu as an inline keyboard.

    FIXED:
    - All logic related to FSM and hardcoded values has been removed.
    - Buttons now use SettingsCallback for navigation, allowing delegation
      of handling to the appropriate modules (game_mode.py, card_theme.py).
    - All text has been translated into Russian for consistency.
    - The use of pony.orm has been replaced with asynchronous calls to Tortoise ORM.
    - Added language selection button.
    """
    builder = InlineKeyboardBuilder()

    # Кнопка для выбора языка
    if user_id:
        current_lang = await language_manager.get_user_language(user_id)
        lang_names = {'uk': 'UA', 'ru': 'RU', 'en': 'EN'}
        current_lang_name = lang_names.get(current_lang, current_lang.upper())
        builder.button(
            text=f"🌐 Мова ({current_lang_name})",
            callback_data=SettingsCallback(level="language").pack()
        )

    # Кнопка для перехода в меню выбора режима игры
    builder.button(
        text=t("buttons.game_mode"),
        callback_data=SettingsCallback(level="gamemode").pack()
    )

    # Кнопка для перехода в меню выбора темы карт
    builder.button(
        text=t("buttons.card_theme"),
        callback_data=SettingsCallback(level="card_theme").pack()
    )

    # Администраторская опция для включения/выключения помощника по ID стикеров
    if is_admin:
        db_chat, _ = await Chat.get_or_create(
            id=chat.id, 
            defaults={'title': chat.title or "Unknown", 'type': chat.type}
        )
        cs, _ = await ChatSetting.get_or_create(chat=db_chat)
        sticker_helper_status = "✅" if cs.sticker_id_helper else "❌"
        
        builder.button(
            text=f"👨‍💻 Помічник ID стикерів ({sticker_helper_status})",
            callback_data=SettingsCallback(level="toggle_sticker_helper").pack(),
        )
    
    builder.adjust(1)
    return builder.as_markup()


@router.message(Command("settings"))
async def settings_command_handler(message: types.Message):
    """
    Обработчик команды /settings.
    Отображает главное меню настроек.

    Handler for the /settings command.
    Displays the main settings menu.
    """
    is_admin = await utils.user_can_change_settings(message.bot, message.from_user.id, message.chat.id)
    await message.answer(
        t("settings.title"),
        reply_markup=await get_main_settings_keyboard(message.chat, is_admin, message.from_user.id),
    )


@router.callback_query(SettingsCallback.filter(F.level == "main_menu"))
async def back_to_main_settings_handler(call: types.CallbackQuery):
    """
    Обработчик для кнопки "Назад", возвращающей в главное меню настроек.

    Handler for the "Back" button, which returns to the main settings menu.
    """
    is_admin = await utils.user_can_change_settings(call.bot, call.from_user.id, call.message.chat.id)
    await call.message.edit_text(
        t("settings.title"),
        reply_markup=await get_main_settings_keyboard(call.message.chat, is_admin, call.from_user.id),
    )
    await call.answer()


@router.callback_query(SettingsCallback.filter(F.level == "toggle_sticker_helper"))
async def toggle_sticker_helper_handler(call: types.CallbackQuery):
    """
    Обработчик для переключения помощника ID стикеров (только для администраторов).

    Handler for toggling the sticker ID helper (admins only).
    """
    if not await utils.user_can_change_settings(call.bot, call.from_user.id, call.message.chat.id):
        await call.answer(t("errors.not_enough_rights"), show_alert=True)
        return

    chat = call.message.chat
    
    db_chat, _ = await Chat.get_or_create(
        id=chat.id,
        defaults={'title': chat.title or "Unknown", 'type': chat.type}
    )
    cs, _ = await ChatSetting.get_or_create(chat=db_chat)
    cs.sticker_id_helper = not cs.sticker_id_helper
    await cs.save()

    new_status = "включен" if cs.sticker_id_helper else "выключен"

    await call.answer(f"Помощник ID стикеров {new_status}")

    # Обновляем клавиатуру, чтобы отразить новое состояние
    # Поскольку этот обработчик доступен только администраторам, мы можем безопасно передать True
    await call.message.edit_reply_markup(
        reply_markup=await get_main_settings_keyboard(chat, True, call.from_user.id)
    )


@router.callback_query(SettingsCallback.filter(F.level == "language"))
async def language_settings_handler(call: types.CallbackQuery):
    """
    Обработчик для меню выбора языка.

    Handler for language selection menu.
    """
    from .language import get_language_keyboard
    
    current_language = await language_manager.get_user_language(call.from_user.id)
    
    await call.message.edit_text(
        "🌐 **Мова / Language**\n\n"
        "Оберіть мову інтерфейсу:\n"
        "Choose your interface language:",
        reply_markup=get_language_keyboard(current_language)
    )
    await call.answer()


@router.callback_query(SettingsCallback.filter(F.level == "set_language"))
async def set_language_handler(call: types.CallbackQuery, callback_data: SettingsCallback):
    """
    Обработчик для установки языка.

    Handler for setting language.
    """
    lang_code = callback_data.value
    
    # Set user language preference
    await language_manager.set_user_language(call.from_user.id, lang_code)
    
    # Update the message
    from .language import get_language_keyboard
    
    await call.message.edit_text(
        "🌐 **Мова / Language**\n\n"
        "Оберіть мову інтерфейсу:\n"
        "Choose your interface language:",
        reply_markup=get_language_keyboard(lang_code)
    )
    
    await call.answer("Мову змінено! / Language changed!")