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
    Темы определяются по наличию .py файлов в директории `durak/objects/decks`.

    Returns a sorted list of available card themes.
    Themes are identified by the presence of .py files in the `durak/objects/decks` directory.
    """
    themes_path = os.path.join("durak", "objects", "decks")
    if not os.path.isdir(themes_path):
        return []
    
    return sorted([
        f.split('.')[0] 
        for f in os.listdir(themes_path) 
        if f.endswith('.py') and not f.startswith('__')
    ])

async def get_card_theme_keyboard(chat: types.Chat):
    """
    Генерирует клавиатуру для настроек темы карт.
    Отмечает текущую выбранную тему.
    
    Generates the keyboard for card theme settings.
    Marks the currently selected theme.
    """
    db_chat, _ = await Chat.get_or_create(
        id=chat.id, 
        defaults={'title': chat.title or "Unknown", 'type': chat.type}
    )
    cs, _ = await ChatSetting.get_or_create(chat=db_chat)
    current_theme = cs.card_theme
    builder = InlineKeyboardBuilder()

    available_themes = get_available_themes()
    if not available_themes:
        builder.row(types.InlineKeyboardButton(
            text="⚠️ Темы не найдены!",
            callback_data="ignore"
        ))
    else:
        for theme_id in available_themes:
            # ИСПРАВЛЕНО: Убрано .capitalize(), чтобы избежать проблем с именами файлов.
            # FIXED: Removed .capitalize() to avoid issues with filenames.
            text = f'''» {theme_id} «''' if current_theme == theme_id else theme_id
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
    db_chat, _ = await Chat.get_or_create(
        id=message.chat.id, 
        defaults={'title': message.chat.title or "Unknown", 'type': message.chat.type}
    )
    chat_setting, _ = await ChatSetting.get_or_create(chat=db_chat)
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
        "🎨 <b>Тема карт</b>\n\nВыберите внешний вид карт:",
        reply_markup=await get_card_theme_keyboard(call.message.chat)
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
    chat = call.message.chat

    db_chat, _ = await Chat.get_or_create(
        id=chat.id, 
        defaults={'title': chat.title or "Unknown", 'type': chat.type}
    )
    chat_setting, _ = await ChatSetting.get_or_create(chat=db_chat)

    if chat_setting.card_theme != new_theme:
        chat_setting.card_theme = new_theme
        await chat_setting.save()
        
        await call.message.edit_reply_markup(
            reply_markup=await get_card_theme_keyboard(chat)
        )
        # ИСПРАВЛЕНО: Убрано .capitalize()
        # FIXED: Removed .capitalize()
        await call.answer(f"✅ Тема изменена на {new_theme}")
    else:
        await call.answer("Эта тема уже установлена")
