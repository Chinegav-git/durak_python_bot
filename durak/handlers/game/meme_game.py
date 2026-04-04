import asyncio
import random
from aiogram import types
from loader import dp, bot
from pony.orm import db_session, commit, select
from durak.db.meme_models import MemeSession, MemeEntry, MemeVote

# Загрузка данных из файлов
def get_memes():
    with open("stickers.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def get_situation():
    with open("situations.txt", "r", encoding="utf-8") as f:
        return random.choice([line.strip() for line in f if line.strip()])

# --- Команда старта ---
@dp.message_handler(commands=['meme'])
@db_session
async def cmd_meme(message: types.Message):
    sit = get_situation()
    MemeSession(chat_id=message.chat.id, situation=sit)
    
    # Кнопка с переходом в инлайн режим именно с префиксом "meme"
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(
        text="🖼 Вибрати мем", 
        switch_inline_query_current_chat="meme" 
    ))
    
    await message.answer(
        f"<b>🎬 ГРА: ЩО ЗА МЕМ?</b>\n\n"
        f"Ситуація:\n«{sit}»\n\n"
        f"⏳ У вас 30 секунд на вибір!", reply_markup=kb
    )
    
    await asyncio.sleep(30)
    await start_meme_voting(message.chat.id)

# --- Инлайн обработчик ---
@dp.inline_handler(lambda q: q.query.startswith('meme'))
async def inline_meme_handler(inline_query: types.InlineQuery):
    offset = int(inline_query.offset) if inline_query.offset else 0
    all_stickers = get_memes()
    
    limit = 8
    next_offset = str(offset + limit) if offset + limit < len(all_stickers) else ""
    current_stickers = all_stickers[offset:offset+limit]

    results = [
        types.InlineQueryResultCachedSticker(
            id=f"m_{offset+i}",
            sticker_file_id=s_id
        ) for i, s_id in enumerate(current_stickers)
    ]

    await bot.answer_inline_query(
        inline_query.id, results=results, 
        cache_time=1, next_offset=next_offset, is_personal=True
    )