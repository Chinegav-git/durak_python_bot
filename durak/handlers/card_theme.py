# -*- coding: utf-8 -*-
"""
Обработчики для настройки темы (внешнего вида) карт.
Позволяет пользователю выбирать и устанавливать тему карт для текущего чата.
Handlers for configuring the card theme (appearance).
Allows the user to select and set the card theme for the current chat.
"""

import os
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from durak.db.models import Chat, ChatSetting
from .settings_callback import SettingsCallback

router = Router()

def get_available_themes():
    """
    Возвращает отсортированный список доступных тем карт.
    Темы определяются по наличию .py файлов в директории `durak/objects/themes`.
    
    ИСПРАВЛЕНО: Путь к темам обновлен с `decks` на `themes`.

    Returns a sorted list of available card themes.
    Themes are identified by the presence of .py files in the `durak/objects/themes` directory.
    
    FIXED: The path to themes has been updated from `decks` to `themes`.
    """
    # ИСПРАВЛЕНО: Путь изменен на корректный
    themes_path = os.path.join("durak", "objects", "themes")
    if not os.path.isdir(themes_path):
        return [] # Возвращаем пустой список, если директория не найдена
    
    return sorted([
        f.split('.')[0] 
        for f in os.listdir(themes_path) 
        if f.endswith('.py') and not f.startswith('__')
    ])

async def get_card_theme_keyboard(chat_id: int):
    """
    Генерирует клавиатуру для настроек темы карт.
    Отмечает текущую выбранную тему.
    Generates the keyboard for card theme settings.
    Marks the currently selected theme.
    """
    chat, _ = await Chat.get_or_create(id=chat_id)
    cs, _ = await ChatSetting.get_or_create(chat=chat)
    current_theme = cs.card_theme
    builder = InlineKeyboardBuilder()

    available_themes = get_available_themes()
    if not available_themes:
        # Если темы не найдены, добавляем сообщение об ошибке
        builder.row(types.InlineKeyboardButton(
            text="⚠️ Теми не знайдено!",
            callback_data="ignore"
        ))
    else:
        for theme_id in available_themes:
            text = f'''» {theme_id.capitalize()} «''' if current_theme == theme_id else theme_id.capitalize()
            builder.button(
                text=text,
                callback_data=SettingsCallback(level="card_theme_select", value=theme_id).pack()
            )
        builder.adjust(2)

    builder.row(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data=SettingsCallback(level="main_menu").pack()
    ))
    return builder.as_markup()


@router.message(Command("cardtheme"))
async def set_card_theme(message: types.Message):
    """
    Обработчик команды /cardtheme.
    Сообщает пользователю текущую тему и предлагает использовать /settings для изменения.
    Handler for the /cardtheme command.
    Informs the user about the current theme and suggests using /settings to change it.
    """
    chat, _ = await Chat.get_or_create(id=message.chat.id)
    chat_setting, _ = await ChatSetting.get_or_create(chat=chat)
    current_theme = chat_setting.card_theme

    await message.answer(
        f"Текущая тема карт: `{current_theme}`.\n\n"
        f"Чтобы изменить тему, воспользуйтесь меню /settings.",
        parse_mode='Markdown'
    )


@router.callback_query(SettingsCallback.filter(F.level == "card_theme"))
async def show_card_theme_settings(call: types.CallbackQuery):
    """
    Показывает меню выбора темы карт по нажатию на кнопку в настройках.
    Shows the card theme selection menu when the button in settings is pressed.
    """
    await call.message.edit_text(
        "🎨 **Тема карт**\n\nВыберите внешний вид карт:",
        reply_markup=await get_card_theme_keyboard(call.message.chat.id)
    )
    await call.answer()


@router.callback_query(SettingsCallback.filter(F.level == "card_theme_select"))
async def set_card_theme_callback(call: types.CallbackQuery, callback_data: SettingsCallback):
    """
    Устанавливает выбранную тему карт из callback'а.
    Обновляет запись в базе данных и изменяет клавиатуру, чтобы отразить выбор.
    Sets the chosen card theme from a callback.
    Updates the database record and modifies the keyboard to reflect the choice.
    """
    new_theme = callback_data.value
    chat_id = call.message.chat.id

    chat, _ = await Chat.get_or_create(id=chat_id)
    chat_setting, _ = await ChatSetting.get_or_create(chat=chat)
    if chat_setting.card_theme != new_theme:
        chat_setting.card_theme = new_theme
        await chat_setting.save()
        await call.answer(f"✅ Тема изменена на {new_theme.capitalize()}")
    else:
        await call.answer("Эта тема уже установлена")

    await call.message.edit_reply_markup(
        reply_markup=await get_card_theme_keyboard(chat_id)
    )
