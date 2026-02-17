from aiogram import types
from aiogram.dispatcher.filters import Command
from loader import dp, gm, Commands
from durak.objects import GameAlreadyInChatError, AlreadyJoinedInGlobalError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@dp.message_handler(Command(Commands.NEW), chat_type=['group', 'supergroup'])
async def new_handler(message: types.Message):
    """ Creating new game """
    user = message.from_user
    chat = message.chat

    try:
        game = await gm.new_game(chat, creator=user)

    except GameAlreadyInChatError:
        await message.answer('🚫 У цьому чаті вже є гра')
        return
    except AlreadyJoinedInGlobalError:
        await message.answer('🚫 Ви вже перебуваєте в іншій грі.')
        return

    join_button = InlineKeyboardButton(text='👋 Приєднатися', callback_data=f'join_game_{game.id}')
    start_button = InlineKeyboardButton(text='🚀 Почати гру', callback_data=f'start_game_{game.id}')
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[join_button], [start_button]])
    
    await message.answer(
        f'🎮 Гру створено!\n'
        f'👤 Засновник: {user.get_mention(as_html=True)}\n\n'
        f'Використовуйте кнопки нижче для керування грою:',
        reply_markup=keyboard
    )
