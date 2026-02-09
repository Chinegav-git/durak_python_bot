from aiogram import types
from loader import bot, dp, gm, Commands
from durak.objects import *
from durak.logic.utils import (
    user_is_admin,
    user_is_creator,
    user_is_bot_admin,
    user_is_creator_or_admin
)


@dp.message_handler(commands=[Commands.KILL], chat_type=['group', 'supergroup'])
async def start_handler(message: types.Message):
    ''' Kill a game '''
    user = types.User.get_current()
    chat = types.Chat.get_current()

    try:
        game = gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await message.answer(f'🚫 У цьому чаті немає гри!\n🎮 Створіть її за допомогою - /{Commands.NEW}')
        return
    
    mention = user.get_mention(as_html=True)

    if (await user_is_creator_or_admin(user, game, chat)):
        # game end
        gm.end_game(chat)
        await message.answer(f'🛑 {mention} завершив(ла) гру!')
        return
    else:
        await message.answer('🚫 Ви не можете завершити гру!')
        return