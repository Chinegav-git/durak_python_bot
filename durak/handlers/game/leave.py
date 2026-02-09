from aiogram import types
from loader import bot, dp, gm, Commands
import durak.logic.actions as a
from durak.objects import *


@dp.message_handler(commands=[Commands.LEAVE], chat_type=['group', 'supergroup'])
async def leave_handler(message: types.Message):
    ''' Leave in a game '''
    user = types.User.get_current()
    chat = types.Chat.get_current()

    try:
        game = gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await message.answer(f'🚫 У цьому чаті немає гри!\n🎮 Створіть її за допомогою - /{Commands.NEW}')
        return
    
    player = gm.player_for_user(user)

    if player is None:
        await message.answer('🚫 Ви не граєте!')
        return
    
    try:
        # kick player
        await a.do_leave_player(player)
    except NotEnoughPlayersError:
        gm.end_game(chat)
        await message.answer('🎮 Гра завершена!')
    else:
        if game.started:
            await message.answer(f'👍 Добре, хід робить гравець {game.current_player.user.get_mention(as_html=True)}')
        else:
            await message.answer(f'👋 ({user.get_mention(as_html=True)}) - Покинув(ла) лобі!')