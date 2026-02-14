from aiogram import types
from aiogram.dispatcher.filters import Command
from pony.orm import db_session

from durak.db.chat_settings import ChatSetting
from durak.logic.utils import user_is_creator
from loader import dp, gm
from durak.objects import NoGameInChatError


@dp.message_handler(Command("gamemode"))
async def set_game_mode(message: types.Message):
    chat_id = message.chat.id
    user = message.from_user
    args = message.get_args()

    reply_message = None

    with db_session:
        try:
            game = gm.get_game_from_chat(message.chat)

            if not user_is_creator(user, game):
                reply_message = "Тільки творець гри може змінювати її режим."
            else:
                chat_setting = ChatSetting.get_or_create(chat_id=chat_id)
                if not args:
                    current_mode = chat_setting.display_mode
                    reply_message = (
                        f"Поточний режим гри: `{current_mode}`\n\n"
                        f"Доступні режими:\n"
                        f"• `text` — класичний текстовий режим\n"
                        f"• `text_and_sticker` — текст та стікери карт\n"
                        f"• `sticker_and_button` — стікери та кнопки (мінімалістично)\n\n"
                        f"Щоб змінити режим, введіть: `/gamemode <назва_режиму>`"
                    )
                else:
                    new_mode = args.lower()
                    if new_mode in ("text", "text_and_sticker", "sticker_and_button"):
                        chat_setting.display_mode = new_mode
                        reply_message = f"✅ Режим гри змінено на `{new_mode}`"
                    else:
                        reply_message = "Невідомий режим. Доступні: `text`, `text_and_sticker`, `sticker_and_button`."

        except NoGameInChatError:
            chat_setting = ChatSetting.get(id=chat_id)
            if chat_setting and chat_setting.is_game_active:
                chat_setting.is_game_active = False  # Reset stale game state
            reply_message = "Гра не створена в цьому чаті."

    if reply_message:
        await message.answer(reply_message)
