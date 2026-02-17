
from aiogram import types
from aiogram.dispatcher.filters import Command
from loader import bot, dp, gm, Commands
from durak.objects import *
import durak.logic.actions as a
from durak.logic.utils import (
    user_is_creator_or_admin
)

@dp.message_handler(Command(Commands.KICK), chat_type=['group', 'supergroup'])
async def kick_handler(message: types.Message):
    """ Kick a player from a game """
    if not message.reply_to_message:
        await message.reply("Ця команда має бути відповіддю на повідомлення гравця, якого ви хочете виключити.")
        return
    
    kicker_user = message.from_user
    kicked_user = message.reply_to_message.from_user
    chat = message.chat

    try:
        game = gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await message.answer(f'🚫 У цьому чаті немає гри!\n🎮 Створіть її за допомогою - /{Commands.NEW}')
        return

    # Check if the user to be kicked is actually in the game
    kicked_player = game.player_for_id(kicked_user.id)
    if not kicked_player:
        await message.reply('🚫 Цей користувач не бере участі в грі.')
        return

    # Check permissions
    # Only the game creator or a chat admin can kick players
    if not await user_is_creator_or_admin(kicker_user, game, chat):
        await message.reply('🚫 Ви не можете виключати гравців. Це може зробити тільки творець гри або адміністратор чату.')
        return

    # Prevent kicking the creator
    if kicked_player.user.id == game.creator.id:
        await message.reply('🚫 Неможливо виключити творця гри.')
        return
    
    kicked_mention = kicked_user.get_mention(as_html=True)
    kicker_mention = kicker_user.get_mention(as_html=True)

    try:
        # The action handles DB updates and game state
        await a.do_leave_player(kicked_player)
    except NotEnoughPlayersError:
        gm.end_game(chat)
        await message.answer(f'👋 {kicked_mention} був(ла) виключений(а) гравцем {kicker_mention}.\n🎮 Гра завершена, оскільки не залишилося гравців!')
    else:
        if game.started:
            await message.answer(f'👋 {kicked_mention} був(ла) виключений(а) гравцем {kicker_mention}.\n🎯 Хід робить гравець {game.current_player.user.get_mention(as_html=True)}')
        else:
            await message.answer(f'👋 {kicked_mention} був(ла) виключений(а) гравцем {kicker_mention} з лоббі!')
