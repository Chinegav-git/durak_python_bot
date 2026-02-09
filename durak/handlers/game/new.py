from aiogram import types
from loader import bot, dp, gm, Commands
from durak.objects import *
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@dp.message_handler(commands=[Commands.NEW], chat_type=['group', 'supergroup'])
async def new_handler(message: types.Message):
    ''' Creating new game '''
    import logging
    logging.info("New game created")
    user = types.User.get_current()
    chat = types.Chat.get_current()

    try:
        # create
        game = gm.new_game(chat, creator=user)
    except GameAlreadyInChatError:
        await message.answer('🚫 У цьому чаті вже є гра')
        return
    
    # Create inline keyboards for join and start
    join_button = InlineKeyboardButton(text='👋 Приєднатися', callback_data=f'join_game_{user.id}')
    start_button = InlineKeyboardButton(text='🚀 Почати гру', callback_data=f'start_game_{user.id}')
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[join_button], [start_button]])
    
    await message.answer(
        f'🎮 Гру створено!\n'
        f'👤 Створець: {user.get_mention(as_html=True)}\n\n'
        f'Використовуйте кнопки нижче для керування грою:',
        reply_markup=keyboard
    )