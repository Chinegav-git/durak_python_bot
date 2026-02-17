from aiogram import types
from pony.orm import db_session

from durak.db import UserSetting
from loader import dp
from durak.handlers.settings import settings_cd

def get_stats_text_and_keyboard(user_id):
    """
    Generates the text and keyboard for the statistics menu.
    """
    with db_session:
        us = UserSetting.get_or_create(id=user_id)
        stat_status_icon = "✅" if us.stats else "❌"
        stat_status_text = "Увімкнений" if us.stats else "Вимкнений"
        
        win_percentage = round((us.first_places / us.games_played) * 100) if us.games_played else 0
        
        text = (
            f"📊 **Ваша статистика**\n\n"
            f"- Статус збору: **{stat_status_text}**\n"
            f"- Перемоги: **{us.first_places}** / {us.games_played} ({win_percentage}%)\n"
            f"- Зроблено ходів: {us.cards_played}\n"
            f"- Відбито карт: {us.cards_beaten}"
        )

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(
        text=f"{stat_status_icon} Збір статистики",
        callback_data=settings_cd.new(level="toggle_stats", value="toggle")
    ))
    markup.add(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data=settings_cd.new(level="main_menu", value="back")
    ))
    return text, markup

@dp.callback_query_handler(settings_cd.filter(level="stats"))
async def show_stats_settings(call: types.CallbackQuery):
    """
    Shows the statistics menu.
    """
    user_id = call.from_user.id
    text, markup = get_stats_text_and_keyboard(user_id)
    
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()

@dp.callback_query_handler(settings_cd.filter(level="toggle_stats"))
async def toggle_stats_callback(call: types.CallbackQuery):
    """
    Toggles statistics collection for the user.
    """
    user_id = call.from_user.id

    with db_session:
        us = UserSetting.get_or_create(id=user_id)
        us.stats = not us.stats
        new_status = "увімкнено" if us.stats else "вимкнено"
    
    await call.answer(f"✅ Збір статистики {new_status}")

    # Update the message with new stats info
    text, markup = get_stats_text_and_keyboard(user_id)
    await call.message.edit_text(text, reply_markup=markup)
