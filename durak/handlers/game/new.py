from aiogram import types
from loader import bot, dp, gm, Commands
from durak.objects import *
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from durak.db import ChatSetting
from pony.orm import db_session

@dp.message_handler(commands=[Commands.NEW], chat_type=['group', 'supergroup'])
async def new_handler(message: types.Message):
    """ Creating new game """
    user = message.from_user
    chat = message.chat
    game = None

    try:
        # SYNCHRONOUS BLOCK: Game creation and DB interaction are isolated.
        with db_session:
            game = gm.new_game(chat, creator=user)

    except GameAlreadyInChatError:
        # ASYNCHRONOUS BLOCK: Safely outside the DB session.
        await message.answer('🚫 У цьому чаті вже є гра')
        return

    # ASYNCHRONOUS BLOCK: All message sending is outside the DB session.
    join_button = InlineKeyboardButton(text='👋 Приєднатися', callback_data=f'join_game_{game.id}')
    start_button = InlineKeyboardButton(text='🚀 Почати гру', callback_data=f'start_game_{game.id}')
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[join_button], [start_button]])
    
    await message.answer(
        f'🎮 Гру створено!\n'
        f'👤 Засновник: {user.get_mention(as_html=True)}\n\n'
        f'Використовуйте кнопки нижче для керування грою:',
        reply_markup=keyboard
    )
