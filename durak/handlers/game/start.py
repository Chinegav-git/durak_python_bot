import asyncio
from aiogram import types, F, Router, Bot
from aiogram.filters import Command
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest

from durak.logic.game_manager import GameManager
from durak.objects import *
from durak.handlers.game import GameCallback
from durak.logic.utils import user_is_creator_or_admin
from durak.db.chat_settings import get_chat_settings
from durak.objects.card import get_sticker_id

router = Router()
gm = GameManager()

async def send_game_start_message(bot: Bot, chat_id: int, game: Game):
    """Sends the initial message when a game starts."""
    # Asynchronously fetch chat settings to get the card theme
    settings = await asyncio.to_thread(get_chat_settings, chat_id)
    theme_name = settings.card_theme if settings else 'classic'
    
    # Get the sticker for the trump suit
    trump_sticker_id = get_sticker_id(game.trump.value, theme_name)

    # Send the trump sticker first, if available
    if trump_sticker_id:
        with suppress(TelegramBadRequest):
            await bot.send_sticker(chat_id, trump_sticker_id)

    # Prepare the game start message
    current = game.current_player
    opponent = game.opponent_player
    text = (
        f'🎯 <b>Початок раунду</b>\n\n'
        f'⚔️ Атакує: {current.get_mention(as_html=True)} (🃏{len(current.cards)})\n'
        f'🛡️ Захищається: {opponent.get_mention(as_html=True)} (🃏{len(opponent.cards)})\n\n'
        f'🃏 Козир: {game.deck.trump_ico}\n'
        f'🃏 В колоді: {len(game.deck.cards)} карт'
    )
    
    # TODO: Replace CHOISE with a dynamic keyboard based on player's hand
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Перевести", callback_data="...")],
        [types.InlineKeyboardButton(text="Взяти карти", callback_data="...")],
    ])
    await bot.send_message(chat_id, text, reply_markup=keyboard)


async def process_start(chat: types.Chat, user: types.User, game_id_from_callback: int = None):
    """Generic function to handle starting a game."""
    try:
        game = await gm.get_game_from_chat(chat)
        if game_id_from_callback and game.id != game_id_from_callback:
            return "Ця кнопка застаріла."
    except NoGameInChatError:
        return f'🚫 У цьому чаті немає гри! Створіть її за допомогою - /new'
    
    if not (await user_is_creator_or_admin(user.id, game, chat.id)):
        return '🚫 Почати гру може лише її творець, адміністратор чату або адміністратор бота.'

    try:
        await gm.start_game(game)
    except GameStartedError:
        return '🎮 Гра вже запущена!'
    except NotEnoughPlayersError:
        return f'🚫 Недостатньо гравців! Приєднатися до гри - /join'
    
    return game # Return game object on success


@router.message(Command("start"), F.chat.type.in_({'group', 'supergroup'}))
async def start_command_handler(message: types.Message, bot: Bot):
    """Handles the /start command."""
    result = await process_start(message.chat, message.from_user)
    
    if isinstance(result, str):
        await message.answer(result)
    else:
        game = result
        await message.answer('🚀 Гра почалася!')
        await send_game_start_message(bot, message.chat.id, game)


@router.callback_query(GameCallback.filter(F.action == "start"))
async def start_callback_handler(call: types.CallbackQuery, callback_data: GameCallback, bot: Bot):
    """Handles the 'Start' button callback."""
    result = await process_start(call.message.chat, call.from_user, callback_data.game_id)
    
    if isinstance(result, str):
        await call.answer(result, show_alert=True)
        return

    game = result
    await call.answer('🚀 Гра почалася!', show_alert=False)
    
    # Delete the lobby message
    with suppress(TelegramBadRequest):
        await call.message.delete()

    await send_game_start_message(bot, call.message.chat.id, game)
