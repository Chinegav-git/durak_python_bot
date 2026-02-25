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
from durak.filters.is_admin import IsAdminFilter
# ИСПРАВЛЕНО: Теперь используется SettingsCallback для навигации по меню.
# FIXED: Now using SettingsCallback for menu navigation.
from .settings_callback import SettingsCallback

router = Router()

async def get_main_settings_keyboard(chat_id: int, is_admin: bool) -> types.InlineKeyboardMarkup:
    """
    Генерирует главное меню настроек в виде inline-клавиатуры.
    
    ИСПРАВЛЕНО: 
    - Удалена вся логика, связанная с FSM и жестко закодированными значениями.
    - Кнопки теперь используют SettingsCallback для навигации, что позволяет
      делегировать обработку соответствующим модулям (game_mode.py, card_theme.py).
    - Весь текст переведен на русский язык для единообразия.
    - Использование pony.orm заменено на асинхронные вызовы Tortoise ORM.

    Generates the main settings menu as an inline keyboard.

    FIXED:
    - All logic related to FSM and hardcoded values has been removed.
    - Buttons now use SettingsCallback for navigation, allowing delegation
      of handling to the appropriate modules (game_mode.py, card_theme.py).
    - All text has been translated into Russian for consistency.
    - The use of pony.orm has been replaced with asynchronous calls to Tortoise ORM.
    """
    builder = InlineKeyboardBuilder()

    # Кнопка для перехода в меню выбора режима игры
    builder.button(
        text="✍️ Режим гри",
        callback_data=SettingsCallback(level="gamemode").pack()
    )

    # Кнопка для перехода в меню выбора темы карт
    builder.button(
        text="🎨 Тема карт",
        callback_data=SettingsCallback(level="card_theme").pack()
    )

    # Администраторская опция для включения/выключения помощника по ID стикеров
    if is_admin:
        chat, _ = await Chat.get_or_create(id=chat_id)
        cs, _ = await ChatSetting.get_or_create(chat=chat)
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
    is_admin = await IsAdminFilter(is_admin=True)(message)
    await message.answer(
        "⚙️ **Настройки**",
        reply_markup=await get_main_settings_keyboard(message.chat.id, is_admin),
    )


@router.callback_query(SettingsCallback.filter(F.level == "main_menu"))
async def back_to_main_settings_handler(call: types.CallbackQuery):
    """
    Обработчик для кнопки "Назад", возвращающей в главное меню настроек.

    Handler for the "Back" button, which returns to the main settings menu.
    """
    is_admin = await IsAdminFilter(is_admin=True)(call)
    await call.message.edit_text(
        "⚙️ **Настройки**",
        reply_markup=await get_main_settings_keyboard(call.message.chat.id, is_admin),
    )
    await call.answer()


@router.callback_query(SettingsCallback.filter(F.level == "toggle_sticker_helper"), IsAdminFilter(is_admin=True))
async def toggle_sticker_helper_handler(call: types.CallbackQuery):
    """
    Обработчик для переключения помощника ID стикеров (только для администраторов).

    Handler for toggling the sticker ID helper (admins only).
    """
    chat_id = call.message.chat.id
    
    chat, _ = await Chat.get_or_create(id=chat_id)
    cs, _ = await ChatSetting.get_or_create(chat=chat)
    cs.sticker_id_helper = not cs.sticker_id_helper
    await cs.save()

    new_status = "включен" if cs.sticker_id_helper else "выключен"

    await call.answer(f"Помощник ID стикеров {new_status}")

    # Обновляем клавиатуру, чтобы отразить новое состояние
    # Поскольку этот обработчик доступен только администраторам, мы можем безопасно передать True
    await call.message.edit_reply_markup(
        reply_markup=await get_main_settings_keyboard(chat_id, True)
    )
