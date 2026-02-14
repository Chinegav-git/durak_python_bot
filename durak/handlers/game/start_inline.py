from aiogram import types
from loader import bot, dp, gm, CHOISE, Commands
from durak.objects import *
from durak.logic.utils import (
    user_is_creator_or_admin
)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('start_game'))
async def start_inline_handler(callback_query: types.CallbackQuery):
    """ Start a game from an inline button """
    user = callback_query.from_user
    chat = callback_query.message.chat

    try:
        game = gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await bot.answer_callback_query(callback_query.id, f'🚫 У цьому чаті немає гри! Створіть її за допомогою - /{Commands.NEW}')
        return

    if not (await user_is_creator_or_admin(user, game, chat)):
        await bot.answer_callback_query(callback_query.id, '🚫 Почати гру може лише її творець, адміністратор чату або адміністратор бота.')
        return
    try:
        # game start
        gm.start_game(game)
    except GameStartedError:
        await bot.answer_callback_query(callback_query.id, '🎮 Гра вже запущена!')
    except NotEnoughPlayersError:
        await bot.answer_callback_query(callback_query.id, f'🚫 Недостатньо гравців! Приєднатися до гри - /{Commands.JOIN}')
    
    else:
        await bot.answer_callback_query(callback_query.id, '🚀 Гра почалася!')
        # Delete the lobby message
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)

        # Send a new message with the game status
        current = game.current_player
        opponent = game.opponent_player
        text = (
            f'🎯 <b>Початок раунду</b>\n\n'
            f'⚔️ <b>Атакує:</b> {current.user.get_mention(as_html=True)} 🃏 {len(current.cards)} карт\n'
            f'🛡️ <b>Захищається:</b> {opponent.user.get_mention(as_html=True)} 🃏 {len(opponent.cards)} карт\n\n'
            f'🎯 <b>Козир:</b> {game.deck.trump_ico}\n'
        )
        await bot.send_message(chat.id, text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=CHOISE))
