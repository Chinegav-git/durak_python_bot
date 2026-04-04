import os
from aiogram import types
from aiogram.dispatcher.filters import Command
from pony.orm import db_session

from durak.db.chat_settings import ChatSetting
from loader import dp


def get_available_themes():
    themes_path = os.path.join("durak", "objects", "decks")
    return sorted([
        f.split('.')[0] 
        for f in os.listdir(themes_path) 
        if f.endswith('.py') and not f.startswith('__')
    ])

@dp.message_handler(Command("cardtheme"))
async def set_card_theme(message: types.Message):
    chat = message.chat
    args = message.get_args()

    available_themes = get_available_themes()
    reply_message = ""

    with db_session:
        chat_setting = ChatSetting.get_or_create(chat.id)
        
        if not args:
            current_theme = chat_setting.card_theme
            themes_list = "\n".join(f"🎨 `/cardtheme {theme}` — {theme.replace('_', ' ').capitalize()}" for theme in available_themes)
            reply_message = (
                f"Поточна тема карт: `{current_theme}`\n\n"
                f"Доступні теми:\n"
                f"{themes_list}\n\n"
                f"Щоб змінити тему, просто натисніть на потрібну команду."
            )
        else:
            new_theme = args.lower()
            if new_theme in available_themes:
                chat_setting.card_theme = new_theme
                reply_message = f"✅ Тему карт змінено на `{new_theme}`"
            else:
                reply_message = f"Невідома тема. Доступні: `{'`, `'.join(available_themes)}`."

    if reply_message:
        await message.answer(reply_message, parse_mode='Markdown')
