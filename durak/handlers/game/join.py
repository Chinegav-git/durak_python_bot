from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest

from durak.logic.game_manager import GameManager
from durak.objects import *
from durak.handlers.game import GameCallback
from config import Config

router = Router()
gm = GameManager()

async def process_join(chat: types.Chat, user: types.User, game_id_from_callback: int = None):
    """A generic function to handle joining a game."""
    try:
        game = await gm.get_game_from_chat(chat)
        if game_id_from_callback and game.id != game_id_from_callback:
            return "Ця кнопка застаріла."
    except NoGameInChatError:
        return f'🚫 У цьому чаті немає гри! Створіть її за допомогою - /new'

    try:
        await gm.join_in_game(game, user)
    except GameStartedError:
        return '🎮 Гра вже запущена! 🚫 Ви не можете приєднатися!'
    except LobbyClosedError:
        return '🚫 Лобі закрито!'
    except LimitPlayersInGameError:
        return f'🚫 Досягнуто ліміт у {Config.MAX_PLAYERS} гравців!'
    except AlreadyJoinedInGlobalError:
        return f'🚫 Схоже ви граєте в іншому чаті! Покинути цю гру - /gleave'
    except AlreadyJoinedError:
        return '🎮 Ви вже в грі!'
    
    return game # Return game object on success

@router.message(Command("join"), F.chat.type.in_({'group', 'supergroup'}))
async def join_command_handler(message: types.Message):
    """Handles the /join command."""
    result = await process_join(message.chat, message.from_user)
    
    if isinstance(result, str):
        await message.answer(result)
    else:
        await message.answer(f'👋 {message.from_user.get_mention(as_html=True)} приєднався до гри!')

@router.callback_query(GameCallback.filter(F.action == "join"))
async def join_callback_handler(call: types.CallbackQuery, callback_data: GameCallback):
    """Handles the 'Join' button callback."""
    result = await process_join(call.message.chat, call.from_user, callback_data.game_id)
    
    if isinstance(result, str):
        await call.answer(result, show_alert=True)
        return

    # On successful join, update the message with the new player list
    game = result
    await call.answer(f'👋 {call.from_user.first_name}, ви приєдналися до гри!', show_alert=False)
    
    players_list = '\n'.join([
        f'{i+1}. {player.get_mention(as_html=True)}'
        for i, player in enumerate(game.players)
    ])
    
    builder = InlineKeyboardBuilder()
    builder.button(text='👋 Приєднатися', callback_data=GameCallback(action="join", game_id=game.id))
    builder.button(text='🚀 Почати гру', callback_data=GameCallback(action="start", game_id=game.id))
    builder.adjust(1)

    with suppress(TelegramBadRequest):
        await call.message.edit_text(
            f'🎮 Гру створено!\n'
            f'👤 Засновник: {game.creator.get_mention(as_html=True)}\n\n'
            f'<b>Гравці:</b>\n{players_list}\n\n'
            f'Використовуйте кнопки нижче для керування грою:',
            reply_markup=builder.as_markup()
        )
