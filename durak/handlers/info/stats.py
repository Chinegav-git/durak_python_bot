from aiogram import Router, types
from aiogram.filters import Command

# It's better to get commands from a single source if they are used across modules
from config import Commands

router = Router()

@router.message(Command(Commands.STATS, Commands.OFF_STATS, Commands.ON_STATS))
async def stats_redirect_handler(message: types.Message):
    """
    Informs user about the new settings menu.
    """
    await message.answer(
        "📊 Керування статистикою було перенесено до єдиного меню налаштувань.\n\n"
        "👉 Будь ласка, скористайтесь командою /settings, щоб переглянути або змінити свої налаштування."
    )
