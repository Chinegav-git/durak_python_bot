from aiogram import types
from loader import bot, dp, gm, CHOISE, Commands
from durak.objects import *
from durak.logic.utils import (
    user_is_admin,
    user_is_creator,
    user_is_bot_admin,
    user_is_creator_or_admin
)


@dp.message_handler(commands=[Commands.START], chat_type=['group', 'supergroup'])
async def start_handler(message: types.Message):
    ''' Start a game '''
    user = types.User.get_current()
    chat = types.Chat.get_current()

    try:
        game = gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await message.answer(f'🚫 У цьому чаті немає гри!\n🎮 Створіть її за допомогою - /{Commands.NEW}')
        return
    
    if not (await user_is_creator_or_admin(user, game, chat)):
        await message.answer('🚫 Ви не можете почати гру!')
        return
    try:
        # game start
        gm.start_game(game)
    except GameStartedError:
        await message.answer('🎮 Гра вже запущена!')
    except NotEnoughPlayersError:
        await message.answer(f'🚫 Недостатньо гравців!\n🎮 Приєднатися до гри - /{Commands.JOIN}')
    
    else:
        await message.answer(f'🎮 Гра почалася!\n\n🎯 Козир - {game.deck.trump_ico}')

        current = game.current_player
        opponent = game.opponent_player
        text = (
            f'🎯 <b>Початок раунду</b>\n\n'
            f'⚔️ <b>Атакує:</b> {current.user.get_mention(as_html=True)} 🃏 {len(current.cards)} карт\n'
            f'🛡️ <b>Захищається:</b> {opponent.user.get_mention(as_html=True)} 🃏 {len(opponent.cards)} карт\n\n'
            f'🎯 <b>Козир:</b> {game.deck.trump_ico}\n'
        )
        await message.answer(text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=CHOISE))