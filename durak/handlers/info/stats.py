from aiogram import types
from loader import dp, Commands

@dp.message_handler(commands=[Commands.STATS, Commands.OFF_STATS, Commands.ON_STATS])
async def stats_redirect_handler(message: types.Message):
    """
    Informs user about the new settings menu.
    """
    await message.answer(
        "📊 Керування статистикою було перенесено до єдиного меню налаштувань.\n\n"
        "👉 Будь ласка, скористайтесь командою /settings, щоб переглянути або змінити свої налаштування."
    )
