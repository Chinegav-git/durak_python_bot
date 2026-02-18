from aiogram import types
from aiogram.dispatcher.filters import Command

from durak.db.models.chat_settings import ChatSetting
from loader import dp
from durak.handlers.settings import settings_cd

async def get_gamemode_keyboard(chat_id):
    """
    Generates the keyboard for game mode settings.
    Marks the current mode.
    """
    cs, _ = await ChatSetting.get_or_create(id=chat_id)
    current_mode = cs.display_mode

    modes = {
        "text": "📝 Текст",
        "text_and_sticker": "🃏 Текст + Стікери",
        "sticker_and_button": "🕹️ Стікери + Кнопки"
    }

    markup = types.InlineKeyboardMarkup(row_width=1)

    for mode_id, mode_name in modes.items():
        text = f"» {mode_name} «" if current_mode == mode_id else mode_name
        markup.add(types.InlineKeyboardButton(
            text=text,
            callback_data=settings_cd.new(level="gamemode_select", value=mode_id)
        ))

    markup.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data=settings_cd.new(level="main_menu", value="back")
    ))
    return markup


@dp.message_handler(Command("gamemode"))
async def set_game_mode(message: types.Message):
    """
    Forwards user to the settings menu
    """
    chat_setting, _ = await ChatSetting.get_or_create(id=message.chat.id)
    current_mode = chat_setting.display_mode

    await message.answer(
        f"Поточний режим гри: `{current_mode}`.\n\n"
        f"Щоб змінити режим, скористайтесь меню /settings.",
        parse_mode='Markdown'
    )


@dp.callback_query_handler(settings_cd.filter(level="gamemode"))
async def show_gamemode_settings(call: types.CallbackQuery):
    """
    Shows the game mode selection menu.
    """
    await call.message.edit_text(
        "✍️ **Режим гри**\n\nОберіть, як будуть відображатись карти та ігровий процес:",
        reply_markup=await get_gamemode_keyboard(call.message.chat.id)
    )
    await call.answer()


@dp.callback_query_handler(settings_cd.filter(level="gamemode_select"))
async def set_gamemode_callback(call: types.CallbackQuery, callback_data: dict):
    """
    Sets the chosen game mode from a callback.
    """
    new_mode = callback_data.get("value")
    chat_id = call.message.chat.id

    chat_setting, _ = await ChatSetting.get_or_create(id=chat_id)
    if chat_setting.display_mode != new_mode:
        chat_setting.display_mode = new_mode
        await chat_setting.save()
        await call.answer("✅ Режим гри змінено")
        
        # Update the keyboard to show the new current mode
        await call.message.edit_reply_markup(
            reply_markup=await get_gamemode_keyboard(chat_id)
        )
    else:
        await call.answer("Цей режим вже встановлено")
