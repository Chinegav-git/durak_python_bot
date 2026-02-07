from aiogram import types
from loader import bot, dp, gm, Commands
from durak.objects import *
import durak.logic.actions as a
from durak.logic.utils import (
    user_is_admin,
    user_is_creator,
    user_is_bot_admin,
    user_is_creator_or_admin
)


@dp.message_handler(commands=[Commands.KICK], chat_type=['group', 'supergroup'])
async def kick_handler(message: types.Message):
    ''' Kick user in a game '''
    reply = message.reply_to_message
    if not reply:
        return
    
    _from_user = types.User.get_current()   # User who kicks out
    _to_user = reply.from_user              # User who is being kicked out
    chat = types.Chat.get_current()

    try:
        game = gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await message.answer(f'🚫 У цьому чаті немає гри!\n🎮 Створіть її за допомогою - /{Commands.NEW}')
        return
    
    _from_player = gm.player_for_user(_from_user)   # Player who kicks out
    _to_player = gm.player_for_user(_to_user)       # Player who is being kicked out

    if _from_player is None:
        if not (await user_is_creator_or_admin(_from_user, game, chat)):
            await message.reply('🚫 Ви не можете видалити цього гравця!')
            return
    else:
        if _from_player.game != game:
            await message.reply('🚫 Ви не можете видалити цього гравця!')
            return
    
    if _to_player is None:
        await message.reply('🚫 Цей користувач не грає!')
        return
    
    if _to_player.game != game:
        await message.reply('🚫 Цей гравець не грає в цьому чаті!')
        return
    
    try:
        # kick player
        await a.do_leave_player(_to_player)
    except NotEnoughPlayersError:
        gm.end_game(chat)
        await message.answer('🎮 Гра завершена!')
    else:
        if game.started:
            await message.answer(f'👍 Добре, хід робить гравець {game.current_player.user.get_mention(as_html=True)}')
        else:
            await message.answer(f'👋 ({_to_user.get_mention(as_html=True)}) був видалений гравцем - {_from_user.get_mention(as_html=True)}!')