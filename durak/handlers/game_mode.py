from aiogram import types
from aiogram.dispatcher.filters import Command

from durak.db.chat_settings import ChatSetting
from durak.db.database import session
from durak.logic.utils import user_is_creator
from loader import dp, gm  # Імпортуємо gm
from durak.objects import NoGameInChatError  # Імпортуємо помилку


@dp.message_handler(Command("gamemode"))
@session
async def set_game_mode(message: types.Message):
    try:
        # Правильно отримуємо гру для поточного чату
        game = gm.get_game_from_chat(message.chat)
    except NoGameInChatError:
        await message.answer("Гра не створена в цьому чаті.")
        return

    if not user_is_creator(message.from_user.id, game):
        await message.answer("Тільки творець гри може змінювати її режим.")
        return

    chat_id = message.chat.id
    # Pony.ORM get_or_create може створювати новий об'єкт, якщо його немає
    chat_setting, _ = ChatSetting.get_or_create(chat_id=chat_id)

    args = message.get_args()
    if not args:
        await message.answer(
            f"Поточний режим гри: `{chat_setting.display_mode}`\n\n"
            f"Доступні режими:\n"
            f"• `text` — класичний текстовий режим\n"
            f"• `text_and_sticker` — текст та стікери карт\n"
            f"• `sticker_and_button` — стікери та кнопки (мінімалістично)\n\n"
            f"Щоб змінити режим, введіть: `/gamemode <назва_режиму>`"
        )
        return

    new_mode = args.lower()
    if new_mode in ("text", "text_and_sticker", "sticker_and_button"):
        chat_setting.display_mode = new_mode
        await message.answer(f"✅ Режим гри змінено на `{new_mode}`")
    else:
        await message.answer("Невідомий режим. Доступні: `text`, `text_and_sticker`, `sticker_and_button`.")
