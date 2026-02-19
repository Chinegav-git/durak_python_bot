from aiogram import Router, types, F
from aiogram.filters import Command

from durak.db.models import ChatSetting
from durak.handlers.settings import SettingsCallback  # Import from settings

router = Router()

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

    builder = types.InlineKeyboardBuilder()

    for mode_id, mode_name in modes.items():
        text = f"» {mode_name} «" if current_mode == mode_id else mode_name
        builder.button(
            text=text,
            callback_data=SettingsCallback(level="gamemode_select", value=mode_id)
        )

    builder.button(
        text="⬅️ Назад",
        callback_data=SettingsCallback(level="main_menu", value="back")
    )
    builder.adjust(1)
    return builder.as_markup()


@router.message(Command("gamemode"))
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


@router.callback_query(SettingsCallback.filter(F.level == "gamemode"))
async def show_gamemode_settings(call: types.CallbackQuery):
    """
    Shows the game mode selection menu.
    """
    await call.message.edit_text(
        "✍️ **Режим гри**\n\nОберіть, як будуть відображатись карти та ігровий процес:",
        reply_markup=await get_gamemode_keyboard(call.message.chat.id)
    )
    await call.answer()


@router.callback_query(SettingsCallback.filter(F.level == "gamemode_select"))
async def set_gamemode_callback(call: types.CallbackQuery, callback_data: SettingsCallback):
    """
    Sets the chosen game mode from a callback.
    """
    new_mode = callback_data.value
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
