import os
from aiogram import types
from aiogram.dispatcher.filters import Command

from durak.db.models.chat_settings import ChatSetting
from loader import dp
from durak.handlers.settings import settings_cd

def get_available_themes():
    """Returns a sorted list of available card themes."""
    themes_path = os.path.join("durak", "objects", "decks")
    return sorted([
        f.split('.')[0] 
        for f in os.listdir(themes_path) 
        if f.endswith('.py') and not f.startswith('__')
    ])

async def get_card_theme_keyboard(chat_id):
    """
    Generates the keyboard for card theme settings.
    Marks the current theme.
    """
    cs, _ = await ChatSetting.get_or_create(id=chat_id)
    current_theme = cs.card_theme

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []

    for theme_id in get_available_themes():
        text = f"» {theme_id.capitalize()} «" if current_theme == theme_id else theme_id.capitalize()
        buttons.append(types.InlineKeyboardButton(
            text=text,
            callback_data=settings_cd.new(level="card_theme_select", value=theme_id)
        ))
    markup.add(*buttons)

    markup.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data=settings_cd.new(level="main_menu", value="back")
    ))
    return markup


@dp.message_handler(Command("cardtheme"))
async def set_card_theme(message: types.Message):
    """
    Forwards user to the settings menu
    """
    chat_setting, _ = await ChatSetting.get_or_create(id=message.chat.id)
    current_theme = chat_setting.card_theme

    await message.answer(
        f"Поточна тема карт: `{current_theme}`.\n\n"
        f"Щоб змінити тему, скористайтесь меню /settings.",
        parse_mode='Markdown'
    )


@dp.callback_query_handler(settings_cd.filter(level="card_theme"))
async def show_card_theme_settings(call: types.CallbackQuery):
    """
    Shows the card theme selection menu.
    """
    await call.message.edit_text(
        "🎨 **Тема карт**\n\nОберіть зовнішній вигляд карт:",
        reply_markup=await get_card_theme_keyboard(call.message.chat.id)
    )
    await call.answer()


@dp.callback_query_handler(settings_cd.filter(level="card_theme_select"))
async def set_card_theme_callback(call: types.CallbackQuery, callback_data: dict):
    """
    Sets the chosen card theme from a callback.
    """
    new_theme = callback_data.get("value")
    chat_id = call.message.chat.id

    chat_setting, _ = await ChatSetting.get_or_create(id=chat_id)
    if chat_setting.card_theme != new_theme:
        chat_setting.card_theme = new_theme
        await chat_setting.save()
        await call.answer(f"✅ Тему змінено на {new_theme.capitalize()}")
    else:
        await call.answer("Ця тема вже встановлена")

    # Update the keyboard to show the new current theme
    await call.message.edit_reply_markup(
        reply_markup=await get_card_theme_keyboard(chat_id)
    )
