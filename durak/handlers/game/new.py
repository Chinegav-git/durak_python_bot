from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from durak.logic.game_manager import GameManager
from durak.objects import GameAlreadyInChatError, AlreadyJoinedInGlobalError
from durak.handlers.game import GameCallback # Import our new CallbackData

router = Router()
gm = GameManager() # Assuming GameManager is our main logic controller

@router.message(Command("new"), F.chat.type.in_({'group', 'supergroup'}))
async def new_game_handler(message: types.Message):
    """
    Handles the /new command to create a new game.
    """
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

    # Build the keyboard with the new CallbackData
    builder = InlineKeyboardBuilder()
    builder.button(
        text='👋 Приєднатися', 
        callback_data=GameCallback(action="join", game_id=game.id)
    )
    builder.button(
        text='🚀 Почати гру', 
        callback_data=GameCallback(action="start", game_id=game.id)
    )
    builder.adjust(1)
    
    await message.answer(
        f'🎮 Гру створено!\n'
        f'👤 Засновник: {user.get_mention(as_html=True)}\n\n'
        f'Використовуйте кнопки нижче для керування грою:',
        reply_markup=builder.as_markup()
    )
