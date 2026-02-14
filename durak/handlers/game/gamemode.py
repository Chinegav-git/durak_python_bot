from aiogram import types, Router
from aiogram.filters import Command, CommandObject
from pony.orm import db_session
from ..db import ChatSetting

router = Router()

@router.message(Command("gamemode"))
@db_session
async def gamemode_handler(message: types.Message, command: CommandObject):
    chat_setting = ChatSetting.get_or_create(message.chat.id)
    
    new_mode = command.args
    available_modes = ['text', 'text_and_sticker', 'sticker_and_button']
    
    if not new_mode:
        # Якщо аргументів немає, показуємо поточний режим та доступні
        response_text = (
            f"Поточний режим гри: *{chat_setting.display_mode}*\n\n"
            f"Доступні режими:\n"
            f"- `text`: лише текст\n"
            f"- `text_and_sticker`: текст та стікери\n"
            f"- `sticker_and_button`: стікери та кнопки\n\n"
            f"Щоб змінити режим, вкажіть його назву, наприклад: `/gamemode text`"
        )
        await message.answer(response_text, parse_mode="Markdown")
        return

    if new_mode in available_modes:
        # Встановлюємо новий режим
        chat_setting.display_mode = new_mode
        await message.answer(f"Режим гри змінено на: *{new_mode}*", parse_mode="Markdown")
    else:
        # Якщо вказано невірний режим
        await message.answer(f"Невідомий режим: `{new_mode}`. Спробуйте один із доступних: `text`, `text_and_sticker`, `sticker_and_button`.")
