from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils.callback_data import CallbackData

from loader import dp

settings_cd = CallbackData("settings", "level", "value")

def get_main_settings_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(
        text="✍️ Режим гри",
        callback_data=settings_cd.new(level="gamemode", value="main")
    ))
    markup.add(types.InlineKeyboardButton(
        text="🎨 Тема карт",
        callback_data=settings_cd.new(level="card_theme", value="main")
    ))
    markup.add(types.InlineKeyboardButton(
        text="📊 Статистика",
        callback_data=settings_cd.new(level="stats", value="main")
    ))
    return markup

@dp.message_handler(Command("settings"))
async def show_settings(message: types.Message):
    """
    Shows the main settings menu
    """
    await message.answer("⚙️ **Налаштування**", reply_markup=get_main_settings_keyboard())

@dp.callback_query_handler(settings_cd.filter(level="main_menu"))
async def show_main_menu(call: types.CallbackQuery):
    """
    Returns to the main settings menu
    """
    await call.message.edit_text("⚙️ **Налаштування**", reply_markup=get_main_settings_keyboard())
    await call.answer()
