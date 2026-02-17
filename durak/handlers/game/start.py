import asyncio
from aiogram import types
from loader import dp, gm, CHOISE, Commands, bot
from durak.objects import (
    NoGameInChatError,
    GameStartedError,
    NotEnoughPlayersError,
    card
)
from durak.logic.utils import (
    user_is_creator_or_admin
)
from durak.db.chat_settings import get_chat_settings


@dp.message_handler(commands=[Commands.START], chat_type=['group', 'supergroup'])
async def start_handler(message: types.Message):
    """ Start a game """ 
    user = message.from_user
    chat = message.chat

    try:
        game = await gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await message.answer(f'🚫 У цьому чаті немає гри!\n🎮 Створіть її за допомогою - /{Commands.NEW}')
        return
    
    if not (await user_is_creator_or_admin(user, game, chat)):
        await message.answer('🚫 Почати гру може лише її творець, адміністратор чату або адміністратор бота.')
        return

    try:
        await gm.start_game(game)
    except (GameStartedError, NotEnoughPlayersError) as e:
        error_messages = {
            GameStartedError: '🎮 Гра вже запущена!',
            NotEnoughPlayersError: f'🚫 Недостатньо гравців!\n🎮 Приєднатися до гри - /{Commands.JOIN}'
        }
        await message.answer(error_messages.get(type(e)))
        return
    
    # Asynchronously fetch chat settings to get the card theme
    settings = await asyncio.to_thread(get_chat_settings, chat.id)
    theme_name = settings.card_theme if settings else 'classic'
    
    # Get the sticker for the trump suit
    trump_sticker_id = card.get_sticker_id(game.trump.value, theme_name)

    # Send the trump sticker first, if available
    if trump_sticker_id:
        await message.answer_sticker(trump_sticker_id)

    # Prepare the game start message
    current = game.current_player
    opponent = game.opponent_player
    text = (
        f'🎯 <b>Початок раунду</b>\n\n'
        f'⚔️ Атакує: {current.user.get_mention(as_html=True)} (🃏{len(current.cards)})\n'
        f'🛡️ Захищається: {opponent.user.get_mention(as_html=True)} (🃏{len(opponent.cards)})\n\n'
        f'🃏 Козир: {game.deck.trump_ico}\n' # Keep the icon for text-based reference
        f'🃏 В колоді: {len(game.deck.cards)} карт'
    )
    
    # Send the main message with the inline keyboard
    await message.answer(text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=CHOISE))
