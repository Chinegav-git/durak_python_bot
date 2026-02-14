from aiogram import types
from durak.db import UserSetting
from loader import bot, dp, Commands
from pony.orm import db_session

def _get_user_stats(user_id):
    with db_session:
        us = UserSetting.get(id=user_id)
        if not us:
            # Create a new setting if it doesn't exist, but don't save it yet
            return UserSetting(id=user_id)
        return us

def _toggle_stats(user_id, status):
    with db_session:
        us = UserSetting.get(id=user_id)
        if not us:
            us = UserSetting(id=user_id)
        us.stats = status

@dp.message_handler(commands=[Commands.STATS])
async def my_stats_handler(message: types.Message):
    user = types.User.get_current()
    
    # SYNCHRONOUS BLOCK
    us = _get_user_stats(user.id)

    stat_status = "✅" if us.stats else "❌"
    
    p = round((us.first_places / us.games_played) * 100) if us.games_played else 0
    
    # ASYNCHRONOUS BLOCK
    await message.answer(f"<u>{stat_status} <b>Ваша статистика:</b></u>\n"
                         f"- Перемоги: {us.first_places} / {us.games_played}   ({p}%)\n"
                         f"- Кількість атак: {us.cards_played}\n"
                         f"- Кількість відбиттів: {us.cards_beaten}")
    

@dp.message_handler(commands=[Commands.OFF_STATS])
async def off_stats_handler(message: types.Message):
    user = types.User.get_current()
    
    # SYNCHRONOUS BLOCK
    _toggle_stats(user.id, False)
        
    # ASYNCHRONOUS BLOCK
    await message.answer(f"<b>Збір статистики припинено!</b>\n<i>Відновити</i> - /{Commands.ON_STATS}")
    
    
@dp.message_handler(commands=[Commands.ON_STATS])
async def on_stats_handler(message: types.Message):
    user = types.User.get_current()
    
    # SYNCHRONOUS BLOCK
    _toggle_stats(user.id, True)
        
    # ASYNCHRONOUS BLOCK
    await message.answer(f"<b>Збір статистики відновлено!</b>\n<i>Припинити</i> - /{Commands.OFF_STATS}")
