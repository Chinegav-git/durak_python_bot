from aiogram import types, Router
from aiogram.filters import Command
from pony.orm import db_session
from ..db import ChatSetting
from ..logic.gamelist import get_gamelist_markup, get_gamelist_text

router = Router()

@router.message(Command("gamemode"))
@db_session
async def gamemode_handler(message: types.Message):
    chat_setting = ChatSetting.get_or_create(message.chat.id)
    
    # Логіка для зміни режиму
    if chat_setting.display_mode == 'text':
        chat_setting.display_mode = 'sticker_and_button'
        response_text = "Режим гри змінено на: *Стікери та кнопки*"
    elif chat_setting.display_mode == 'sticker_and_button':
        chat_setting.display_mode = 'text_and_sticker'
        response_text = "Режим гри змінено на: *Текст та стікери*"
    else: # text_and_sticker
        chat_setting.display_mode = 'text'
        response_text = "Режим гри змінено на: *Лише текст*"

    await message.answer(response_text, parse_mode="Markdown")
