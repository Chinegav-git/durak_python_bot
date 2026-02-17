
from aiogram import types
from aiogram.dispatcher.filters import Command
from loader import bot, dp, gm, Commands
from durak.objects import *
from durak.logic.utils import (
    user_is_creator_or_admin
)


@dp.message_handler(Command(Commands.KILL), chat_type=['group', 'supergroup'])
async def start_handler(message: types.Message):
    ''' Kill a game '''
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        game = gm.get_game_from_chat(chat_id)
    except NoGameInChatError:
        await message.answer(f'🚫 У цьому чаті немає гри!\n🎮 Створіть її за допомогою - /{Commands.NEW}')
        return
    
    mention = message.from_user.get_mention(as_html=True)

    if (await user_is_creator_or_admin(user_id, game)):
        # game end
        gm.end_game(chat_id)
        await message.answer(f'🛑 {mention} завершив(ла) гру!')
        return
    else:
        await message.answer('🚫 Ви не можете завершити гру!')
        return