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
    """ Start a game """
    user = message.from_user
    chat = message.chat

    try:
        game = gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await message.answer(f'🚫 У цьому чаті немає гри!\n🎮 Створіть її за допомогою - /{Commands.NEW}')
        return
    
    if not (await user_is_creator_or_admin(user, game, chat)):
        await message.answer('🚫 Почати гру може лише її творець, адміністратор чату або адміністратор бота.')
        return
    try:
        # game start
        gm.start_game(game)
    except GameStartedError:
        await message.answer('🎮 Гра вже запущена!')
    except NotEnoughPlayersError:
        await message.answer(f'🚫 Недостатньо гравців!\n🎮 Приєднатися до гри - /{Commands.JOIN}')
    
    else:
        # Send a single, consistent start message
        current = game.current_player
        opponent = game.opponent_player
        text = (
            f'🎯 <b>Початок раунду</b>\n\n'
            f'⚔️ Атакує: {current.user.get_mention(as_html=True)} (🃏{len(current.cards)})\n'
            f'🛡️ Захищається: {opponent.user.get_mention(as_html=True)} (🃏{len(opponent.cards)})\n\n'
            f'♦️ Козир: {game.deck.trump_ico}\n'
            f'🃏 В колоді: {len(game.deck.cards)} карт'
        )
        await message.answer(text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=CHOISE))
