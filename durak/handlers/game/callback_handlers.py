from aiogram import types
from aiogram.types import CallbackQuery
from loader import bot, dp, gm, Config, Commands, CHOISE
from durak.objects import *
import durak.logic.actions as a


@dp.callback_query_handler(lambda call: call.data and call.data.startswith('join_game_'))
async def join_callback_handler(call: CallbackQuery):
    """ Handle join button callback """
    user = types.User.get_current()
    chat = call.message.chat
    
    try:
        game = gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await call.answer('🚫 У цьому чаті немає гри!', show_alert=True)
        return
    
    # Extract creator ID from callback data
    creator_id = int(call.data.split('_')[2])
    
    # Verify the game creator matches
    if game.creator.id != creator_id:
        await call.answer('🚫 Ця гра не належить вам!', show_alert=True)
        return
    
    try:
        # add user in a game
        gm.join_in_game(game, user)
        await call.answer('👋 Ви приєдналися до гри!', show_alert=True)
        
        # Update the message to show current players
        players_list = '\n'.join([f'👤 {p.user.get_mention(as_html=True)}' for p in game.players])
        await bot.edit_message_text(
            chat_id=chat.id,
            message_id=call.message.message_id,
            text=f'🎮 Гру створено!\n'
                 f'👤 Створювач: {game.creator.get_mention(as_html=True)}\n\n'
                 f'👥 Гравці ({len(game.players)}/{Config.MAX_PLAYERS}):\n{players_list}\n\n'
                 f'Використовуйте кнопки нижче для керування грою:',
            reply_markup=call.message.reply_markup
        )
        
    except GameStartedError:
        await call.answer('🎮 Гра вже запущена! 🚫 Ви не можете приєднатися!', show_alert=True)
    except LobbyClosedError:
        await call.answer('🚫 Лобі закрито!\n🔓 Відкрити - /open', show_alert=True)
    except LimitPlayersInGameError:
        await call.answer(f'🚫 Досягнуто ліміт у {Config.MAX_PLAYERS} гравців!', show_alert=True)
    except AlreadyJoinedInGlobalError:
        await call.answer(f'🚫 Схоже ви граєте в іншому чаті!\n👋 Покинути цю гру - /{Commands.GLEAVE}', show_alert=True)
    except AlreadyJoinedError:
        await call.answer('🎮 Ви вже в грі!', show_alert=True)


@dp.callback_query_handler(lambda call: call.data and call.data.startswith('start_game_'))
async def start_callback_handler(call: CallbackQuery):
    """ Handle start game button callback """
    user = types.User.get_current()
    chat = call.message.chat
    
    try:
        game = gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await call.answer('🚫 У цьому чаті немає гри!', show_alert=True)
        return
    
    # Extract creator ID from callback data
    creator_id = int(call.data.split('_')[2])
    
    # Check if user is creator or admin
    if game.creator.id != creator_id:
        await call.answer('🚫 Тільки творець гри може запустити її!', show_alert=True)
        return
    
    # Check if user has admin rights (optional enhancement)
    from durak.logic.utils import user_is_creator_or_admin
    if not (await user_is_creator_or_admin(user, game, chat)):
        await call.answer('🚫 Ви не можете почати гру!', show_alert=True)
        return
    
    try:
        # game start
        gm.start_game(game)
        await call.answer('🚀 Гра запущена!', show_alert=True)
        
        # Update the message to show game started
        await bot.edit_message_text(
            chat_id=chat.id,
            message_id=call.message.message_id,
            text=f'🎮 Гра запущена!\n\n'
                 f'🎯 Козир - {game.deck.trump_ico}\n'
                 f'👥 Гравці ({len(game.players)}):\n'
                 + '\n'.join([f'👤 {p.user.get_mention(as_html=True)}' for p in game.players]),
            reply_markup=None  # Remove buttons after game starts
        )
        
        current = game.current_player
        opponent = game.opponent_player
        text = (
            f'🎯 <b>Початок раунду</b>\n\n'
            f'⚔️ <b>Атакує:</b> {current.user.get_mention(as_html=True)} 🃏 {len(current.cards)} карт\n'
            f'🛡️ <b>Захищається:</b> {opponent.user.get_mention(as_html=True)} 🃏 {len(opponent.cards)} карт\n\n'
            f'🎯 <b>Козир:</b> {game.deck.trump_ico}\n'
        )
        await bot.send_message(
            chat.id,
            text,
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=CHOISE)
        )
        
    except GameStartedError:
        await call.answer('🎮 Гра вже запущена!', show_alert=True)
    except NotEnoughPlayersError:
        await call.answer(f'🚫 Недостатньо гравців!\n🎮 Потрібно хоча б 2 гравці', show_alert=True)
