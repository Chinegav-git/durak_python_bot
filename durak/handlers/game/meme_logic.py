import asyncio
from aiogram import types
from loader import dp, bot
from pony.orm import db_session, commit, select
from durak.db.meme_models import MemeSession, MemeEntry, MemeVote

async def run_voting(chat_id: int):
    session = MemeSession.get(chat_id=chat_id, status='gathering')
    if not session: return

    # Тільки ті, хто в грі та надіслав мем
    active_entries = [e for e in session.entries if e.sticker_id and not e.is_out]

    if len(active_entries) < 2:
        session.status = 'finished'
        commit() # <--- Зберігаємо статус ПЕРЕД відправкою повідомлення
        return await bot.send_message(chat_id, "❌ Недостатньо учасників для продовження.")

    session.status = 'voting'
    commit() # <--- КРИТИЧНО: Зберігаємо ПЕРЕД bot.send_message та sleep

    text = "<b>🗳 ГОЛОСУВАННЯ (1 ХВИЛИНА)</b>\n\nХто скинув <b>НАЙГІРШИЙ</b> мем? Оберіть жертву для вильоту:"
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    for entry in active_entries:
        kb.insert(types.InlineKeyboardButton(f"❌ {entry.player_name}", callback_data=f"mvote_{entry.id}"))

    await bot.send_message(chat_id, text, reply_markup=kb)
    
    # Pony ORM "засинає" тут, тому ми зробили commit() вище
    await asyncio.sleep(60) 
    await process_elimination(chat_id)

async def process_elimination(chat_id: int):
    session = MemeSession.get(chat_id=chat_id, status='voting')
    if not session: return

    # Рахуємо голоси (використовуємо .votes.count() для надійності)
    results = sorted([e for e in session.entries if not e.is_out and e.sticker_id], 
                     key=lambda e: len(e.votes), reverse=True)
    
    msg_out = ""
    if not results or len(results[0].votes) == 0:
        msg_out = "ℹ️ Голосів немає. Раунд завершено без вильотів."
    else:
        loser = results[0]
        loser.is_out = True
        msg_out = f"💀 <b>{loser.player_name}</b> вилітає з гри! Твій мем був найменш смішним."

    # Очищення для наступного раунду (змінюємо об'єкти)
    for e in session.entries:
        e.votes.clear()
        e.sticker_id = None 
    
    commit() # <--- КРИТИЧНО: Зберігаємо вибулого та очищення перед повідомленням

    await bot.send_message(chat_id, msg_out)

    # Перевірка на переможця
    remaining = [e for e in session.entries if not e.is_out]
    
    if len(remaining) <= 1:
        winner = remaining[0] if remaining else None
        session.status = 'finished'
        commit() # <--- Зберігаємо статус фінішу
        win_text = f"👑 <b>ПЕРЕМОЖЕЦЬ: {winner.player_name}!</b>" if winner else "Гра завершена."
        return await bot.send_message(chat_id, win_text)

    await bot.send_message(chat_id, "🔄 <b>Наступний раунд через 5 секунд...</b>")
    
    # Pony знову засне, тому транзакція має бути порожньою (ми вже зробили commit)
    await asyncio.sleep(5)
    
    # Автоматичний старт наступного раунду
    from .meme_game import start_new_round_auto
    await start_new_round_auto(chat_id)

@dp.callback_query_handler(lambda c: c.data.startswith("mvote_"))
@db_session
async def handle_meme_vote(call: types.CallbackQuery):
    entry_id = int(call.data.split("_")[1])
    target_entry = MemeEntry.get(id=entry_id)
    
    if not target_entry or target_entry.session.status != 'voting':
        return await call.answer("Голосування вже закінчено!")

    # Перевірка: чи голосував він вже в цій сесії
    any_vote = select(v for v in MemeVote if v.voter_id == call.from_user.id and v.entry.session == target_entry.session).first()

    if any_vote:
        return await call.answer("Ви вже голосували!", show_alert=True)

    # Створюємо новий голос (це зміна в БД)
    MemeVote(voter_id=call.from_user.id, entry=target_entry)
    
    commit() # <--- КРИТИЧНО: Зберігаємо голос ПЕРЕД call.answer (який є await)
    
    await call.answer(f"Голос прийнято!")
