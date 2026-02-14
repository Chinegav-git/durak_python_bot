from aiogram import types
from aiogram.dispatcher.filters import Command
from pony.orm import db_session

from durak.db.chat_settings import ChatSetting
# from durak.logic.utils import user_can_change_gamemode
from loader import dp


@dp.message_handler(Command("gamemode"))
async def set_game_mode(message: types.Message):
    chat = message.chat
    user = message.from_user
    args = message.get_args()

    # First, check permissions.
    # This is an async operation and must be outside a db_session.
    # if not await user_can_change_gamemode(user, chat):
    #     await message.answer("🚫 Тільки адміністратор чату може змінювати режим гри.")
    #     return

    # All database operations are now grouped in one synchronous block.
    reply_message = ""
    with db_session:
        chat_setting = ChatSetting.get_or_create(chat.id)
        
        if not args:
            current_mode = chat_setting.display_mode
            reply_message = (
                f"Поточний режим гри: `{current_mode}`\n\n"
                f"Доступні режими:\n"
                f"📝 `/gamemode text` — класичний текстовий режим\n"
                f"🃏 `/gamemode text_and_sticker` — текст та стікери карт\n"
                f"🕹️ `/gamemode sticker_and_button` — стікери та кнопки (мінімалістично)\n\n"
                f"Щоб змінити режим, просто натисніть на потрібну команду."
            )
        else:
            new_mode = args.lower()
            if new_mode in ("text", "text_and_sticker", "sticker_and_button"):
                chat_setting.display_mode = new_mode
                reply_message = f"✅ Режим гри змінено на `{new_mode}`"
            else:
                reply_message = "Невідомий режим. Доступні: `text`, `text_and_sticker`, `sticker_and_button`."

    # The async operation (sending a message) is now safely outside the db_session.
    if reply_message:
        await message.answer(reply_message, parse_mode='Markdown')
