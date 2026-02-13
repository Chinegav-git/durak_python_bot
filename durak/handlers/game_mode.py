from aiogram import types, Router
from aiogram.filters import Command
from ..db import ChatSetting, session
from ..logic.game_manager import gm

gamemode_router = Router()


@gamemode_router.message(Command("gamemode"))
async def cmd_gamemode(message: types.Message):
    game = gm.get_game_from_chat(message.chat)
    if not game:
        return await message.reply("🎮 Гра ще не створена!\nСтворіть гру за допомогою /newgame")

    if message.from_user.id != game.creator.id:
        return await message.reply("💡 Лише творець гри може змінювати її налаштування.")

    args = message.text.split()
    if len(args) == 1:
        chat_settings = ChatSetting.get_or_create(message.chat.id)
        return await message.reply(
            f"Поточний режим відображення: <b>{chat_settings.display_mode}</b>\n\n"
            f"Доступні режими:\n"
            f"• <code>text</code> - класичний текстовий режим\n"
            f"• <code>text_and_sticker</code> - текст зі стікером підкинутої карти\n"
            f"• <code>sticker_and_button</code> - стікер карти та кнопка для дії\n\n"
            f"Щоб змінити режим, введіть команду з назвою режиму, наприклад:\n"
            f"<code>/gamemode text_and_sticker</code>"
        )

    new_mode = args[1]
    if new_mode not in ['text', 'text_and_sticker', 'sticker_and_button']:
        return await message.reply("😕 Невідомий режим. Доступні: text, text_and_sticker, sticker_and_button")

    with session:
        chat_settings = ChatSetting.get_or_create(message.chat.id)
        chat_settings.display_mode = new_mode

    await message.reply(f"✅ Режим відображення гри змінено на <b>{new_mode}</b>")
