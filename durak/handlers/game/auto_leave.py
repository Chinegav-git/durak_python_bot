from aiogram import types
from loader import bot, dp, gm
import durak.logic.actions as a
from durak.objects import *


@dp.message_handler(content_types=[types.ContentTypes.LEFT_CHAT_MEMBER], chat_type=['group', 'supergroup'])
async def auto_leave_handler(message: types.Message):
    ''' Automatic kick players (left from the group) '''
    user = message.left_chat_member
    chat = types.Chat.get_current()

    if not user:
        return
    
    try:
        game = gm.get_game_from_chat(chat)
    except NoGameInChatError:
        return
    
    mention = user.get_mention(as_html=True)
    player = gm.player_for_user(user)

    if player is None:
        return
    
    if player.game != game:
        return

    try:
        # kick player
        await a.do_leave_player(player)
    except NotEnoughPlayersError:
        gm.end_game(chat)
        await bot.send_message(chat.id, f'👋 ({mention}) - Покинув(ла) гру!')
        await bot.send_message(chat.id, '🎮 Гра завершена!\n')
    else:
        if game.started:
            await bot.send_message(chat.id, f'👋 ({mention}) - Покинув(ла) гру\n🎯 Хід робить гравець {game.current_player.user.get_mention(as_html=True)}')
        else:
            await bot.send_message(chat.id, f'👋 ({mention}) - Покинув(ла) лобі!')