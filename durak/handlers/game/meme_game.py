import asyncio
import random
import os
from aiogram import types
from loader import dp, bot
from pony.orm import db_session, commit, select
from durak.db.meme_models import MemeSession, MemeEntry

# --- ДОПОМІЖНІ ФУНКЦІЇ ---
def get_random_sit():
    """Вибирає випадкову ситуацію з файлу."""
    try:
        if not os.path.exists("situations.txt"):
            return "Ситуація: Коли файл situations.txt забули створити 🤡"
        with open("situations.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            return random.choice(lines) if lines else "Ситуація не знайдена"
    except Exception as e:
        print(f"Помилка читання ситуацій: {e}")
        return "Сталася помилка при завантаженні ситуації"

def get_memes_list():
    """Читає список ID стікерів з файлу."""
    try:
        if not os.path.exists("stickers.txt"):
            return []
        with open("stickers.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Помилка читання стікерів: {e}")
        return []

@db_session
async def start_new_round_auto(chat_id: int):
    """Автоматичний запуск наступного раунду битви на виліт."""
    session = MemeSession.get(chat_id=chat_id)
    if not session:
        return

    session.situation = get_random_sit()
    session.status = 'gathering'
    
    # Очищаємо вибір стікерів у тих, хто ще в грі
    for entry in session.entries:
        entry.sticker_id = None
    
    commit() # <--- Зберігаємо зміни ПЕРЕД відправкою повідомлення (await)

    kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🖼 МОЯ РУКА (8 мевів)", switch_inline_query_current_chat="meme")
    )
    
    await bot.send_message(
        chat_id,
        f"<b>🎬 НОВИЙ РАУНД!</b>\n\nСитуація:\n«<b>{session.situation}</b>»\n\n"
        f"⏳ У вас 45 секунд, щоб кинути мем!",
        reply_markup=kb
    )
    
    await asyncio.sleep(45)
    
    from .meme_logic import run_voting 
    await run_voting(chat_id)

# --- ХЕНДЛЕРИ ГРИ ---

@dp.message_handler(commands=['meme'])
@db_session
async def cmd_meme_start(message: types.Message):
    """Створює лобі гри."""
    active = MemeSession.get(chat_id=message.chat.id, status='lobby')
    if active:
        return await message.answer("Лобі вже створено! Натискайте 'Приєднатися'.")

    MemeSession(chat_id=message.chat.id, situation="Очікування гравців...", status='lobby')
    commit() # <--- Зберігаємо ПЕРЕД await message.answer
    
    kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("👋 Приєднатися", callback_data="meme_join")
    )
    await message.answer(
        "<b>🎮 ГРА: БИТВА МЕМІВ (НА ВИЛІТ)</b>\n\nНатисніть кнопку, щоб увійти (мін. 2 гравці).", 
        reply_markup=kb
    )

@dp.callback_query_handler(lambda c: c.data == "meme_join")
@db_session
async def meme_join(call: types.CallbackQuery):
    """Додає гравця в лобі."""
    session = MemeSession.get(chat_id=call.message.chat.id, status='lobby')
    if not session: 
        return await call.answer("Лобі вже закрите!")
    
    if MemeEntry.get(session=session, player_id=call.from_user.id):
        return await call.answer("Ви вже у грі!", show_alert=True)

    all_m = get_memes_list()
    if len(all_m) < 8:
        return await call.answer(f"Мало мевів у базі ({len(all_m)}/8)!", show_alert=True)

    hand = random.sample(all_m, 8)
    
    MemeEntry(
        player_id=call.from_user.id,
        player_name=call.from_user.first_name,
        hand=",".join(hand),
        session=session,
        is_out=False
    )
    commit() # <--- КРИТИЧНО: Зберігаємо гравця перед БУДЬ-ЯКИМ await (навіть call.answer)
    
    await call.answer("Ви у грі!")
    
    count = len(session.entries)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("👋 Приєднатися", callback_data="meme_join"))
    
    if count >= 2:
        kb.add(types.InlineKeyboardButton("🚀 Почати битву", callback_data="meme_start_round"))

    await call.message.edit_text(
        f"<b>🎮 ЛОБІ ГРИ</b>\n\nГравців: <b>{count}</b>\n\nГотові вилітати?",
        reply_markup=kb
    )

@dp.callback_query_handler(lambda c: c.data == "meme_start_round")
@db_session
async def start_round(call: types.CallbackQuery):
    """Перший запуск раунду з лобі."""
    session = MemeSession.get(chat_id=call.message.chat.id, status='lobby')
    if not session:
        return await call.answer("Гру вже запущено.")

    if len(session.entries) < 2: 
        return await call.answer("Треба мінімум 2 людини!")

    session.situation = get_random_sit()
    session.status = 'gathering'
    commit() # <--- Зберігаємо статус ПЕРЕД edit_text
    
    kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🖼 МОЯ РУКА (8 мевів)", switch_inline_query_current_chat="meme")
    )
    
    await call.message.edit_text(
        f"<b>🎬 БИТВА ПОЧАЛАСЯ!</b>\n\nСитуація:\n«<b>{session.situation}</b>»\n\n⏳ У вас 45 секунд!",
        reply_markup=kb
    )
    
    await asyncio.sleep(45)
    
    from .meme_logic import run_voting 
    await run_voting(call.message.chat.id)

@dp.message_handler(content_types=types.ContentType.STICKER)
@db_session
async def handle_sticker_logic(message: types.Message):
    if message.chat.type == 'private':
        sticker_id = message.sticker.file_id
        existing = get_memes_list()
        if sticker_id not in existing:
            with open("stickers.txt", "a", encoding="utf-8") as f:
                f.write(f"{sticker_id}\n")
            return await message.reply(f"✅ Додано!")
        return await message.reply("⚠️ Вже є.")

    session = MemeSession.get(chat_id=message.chat.id, status='gathering')
    if not session: return

    entry = MemeEntry.get(session=session, player_id=message.from_user.id)
    if not entry or entry.is_out or entry.sticker_id: return 

    hand_list = entry.hand.split(",")
    if message.sticker.file_id not in hand_list:
        return await message.reply("❌ Не з вашої руки!")

    entry.sticker_id = message.sticker.file_id
    commit() # <--- Зберігаємо ПЕРЕД відповіддю бота
    await message.answer(f"✅ Мем від <b>{message.from_user.first_name}</b> прийнято!")

# --- НОВИЙ INLINE HANDLER ---
@dp.inline_handler(lambda iq: iq.query == "meme")
@db_session
async def meme_inline_handler(query: types.InlineQuery):
    """
    Відповідає на інлайн-запит "meme", показуючи гравцю його карти (стікери).
    Inline-запити не мають контексту чату, тому для пошуку гри використовується
    ID користувача. Це може призвести до некоректної поведінки, якщо
    користувач грає в кількох чатах одночасно.
    """
    user_id = query.from_user.id
    
    # Шукаємо останню активну гру, де гравець не вилетів.
    entry = select(
        e for e in MemeEntry if e.player_id == user_id and e.session.status == 'gathering' and not e.is_out
    ).order_by(lambda e: e.session.id).first()

    if not entry or not entry.hand:
        return await query.answer([], cache_time=1, is_personal=True,
                                  switch_pm_text="Не вдалося знайти вашу руку в активній грі.",
                                  switch_pm_parameter="start")

    hand_list = entry.hand.split(',')
    
    results = []
    for i, sticker_id in enumerate(hand_list):
        results.append(types.InlineQueryResultCachedSticker(
            id=str(i), # ID результату має бути унікальним string
            sticker_file_id=sticker_id
        ))
        
    await query.answer(results, is_personal=True, cache_time=1)