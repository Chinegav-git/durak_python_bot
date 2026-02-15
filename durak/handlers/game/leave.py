from aiogram import types
from loader import bot, dp, gm, Commands
import durak.logic.actions as a
from durak.objects import *
from pony.orm import db_session

@dp.message_handler(commands=[Commands.LEAVE], chat_type=['group', 'supergroup'])
async def leave_handler(message: types.Message):
    """ Leave a game """
    user = types.User.get_current()
    chat = types.Chat.get_current()

    try:
        game = gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await message.answer(f'🚫 У цьому чаті немає гри!\n🎮 Створіть її за допомогою - /{Commands.NEW}')
        return

    player = game.player_for_user(user)

    if player is None:
        await message.answer('🚫 Ви не в цій грі!')
        return

    try:
        # This action now needs to handle the DB update
        await a.do_leave_player(player)
    except NotEnoughPlayersError:
        # end_game now handles all DB updates for all players
        gm.end_game(chat)
        await message.answer('🎮 Гра завершена, оскільки гравців не залишилося!')
    else:
        if game.started:
            await message.answer(f'👍 Добре, хід робить гравець {game.current_player.user.get_mention(as_html=True)}')
        else:
            await message.answer(f'👋 ({user.get_mention(as_html=True)}) - Покинув(ла) лобі!')
