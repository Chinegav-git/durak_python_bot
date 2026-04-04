@dp.message_handler(content_types=types.ContentType.STICKER)
@db_session
async def collect_meme_sticker(message: types.Message):
    # Проверяем, идет ли стадия сбора
    session = MemeSession.get(chat_id=message.chat.id, status='gathering')
    if not session: return

    # Проверяем, не голосовал ли уже
    if MemeEntry.get(session=session, player_id=message.from_user.id):
        return

    MemeEntry(
        player_id=message.from_user.id,
        player_name=message.from_user.full_name,
        sticker_id=message.sticker.file_id,
        session=session
    )
    await message.reply(f"✅ {message.from_user.first_name}, прийнято!")

@db_session
async def start_meme_voting(chat_id):
    session = MemeSession.get(chat_id=chat_id, status='gathering')
    if not session or not session.entries:
        return await bot.send_message(chat_id, "Ніхто не встиг надіслати мем 😢")

    session.status = 'voting'
    await bot.send_message(chat_id, "<b>ЧАС ВИЙШОВ!</b>\nГолосуємо за НАЙГІРШИЙ мем (хто програв):")

    for entry in session.entries:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("👎 Проголосувати", callback_data=f"mvote_{entry.id}"))
        await bot.send_sticker(chat_id, entry.sticker_id, reply_markup=kb)

    await asyncio.sleep(20)
    await finish_meme_game(chat_id)

@dp.callback_query_handler(lambda c: c.data.startswith('mvote_'))
@db_session
async def handle_meme_vote(call: types.CallbackQuery):
    entry_id = int(call.data.split('_')[1])
    entry = MemeEntry.get(id=entry_id)
    
    # Запрет голосовать за себя и повторно (как в прошлых советах)
    if MemeVote.get(voter_id=call.from_user.id, entry__session=entry.session):
        return await call.answer("Ви вже голосували!", show_alert=True)
        
    MemeVote(voter_id=call.from_user.id, entry=entry)
    await call.answer("Голос враховано!")

@db_session
async def finish_meme_game(chat_id):
    session = MemeSession.get(chat_id=chat_id, status='voting')
    session.status = 'finished'
    
    # Сортировка по количеству голосов
    res = sorted(session.entries, key=lambda e: len(e.votes), reverse=True)
    
    winner_text = "<b>РЕЗУЛЬТАТИ ГОЛОСУВАННЯ:</b>\n\n"
    for e in res:
        winner_text += f"• {e.player_name}: {len(e.votes)} 👎\n"
    
    loser = res[0]
    winner_text += f"\n💀 Найгірший мем у: {loser.player_name}"
    
    await bot.send_message(chat_id, winner_text)