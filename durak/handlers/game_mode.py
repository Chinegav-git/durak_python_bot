from aiogram import types
from loader import dp
from durak.db.db_api import get_chat_setting, set_chat_setting
from durak.filters import IsAdminFilter


@dp.message_handler(commands=['gamemode'], is_admin=True)
async def set_gamemode(message: types.Message):
    try:
        new_mode = message.text.split()[1]
        set_chat_setting(message.chat.id, display_mode=new_mode)
        await message.reply(f'Режим гри змінено на "{new_mode}" для цього чату.')
    except (IndexError, ValueError):
        current_mode = get_chat_setting(message.chat.id).display_mode
        await message.reply(
            f'Поточний режим гри: "{current_mode}".\n'
            f'Використання: /gamemode [text | text_and_sticker | sticker_and_button]'
        )
