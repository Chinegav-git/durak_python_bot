
from aiogram import types
from aiogram.dispatcher.filters import Command
from loader import bot, dp, gm, Commands
import durak.logic.actions as a
from durak.objects import *
from pony.orm import db_session

@dp.message_handler(Command(Commands.GLEAVE), chat_type=['group', 'supergroup'])
async def global_leave_handler(message: types.Message):
    """ Global leave from any game """
    user = types.User.get_current()
    
    player_to_leave = None
    game_to_leave = None

    # Find the player and game across all active games
    for game in gm.games.values():
        for player in game.players:
            if player.id == user.id:
                player_to_leave = player
                game_to_leave = game
                break
        if game_to_leave:
            break

    if not player_to_leave or not game_to_leave:
        await message.answer('🚫 Ви не граєте в жодній грі!')
        return
    
    mention = user.get_mention(as_html=True)

    try:
        # The action now correctly updates the DB
        await a.do_leave_player(player_to_leave)
        await message.answer(f'👋 ({mention}) - Ви успішно покинули гру в іншому чаті!')

    except NotEnoughPlayersError:
        # end_game handles all cleanup
        await gm.end_game(game_to_leave.chat)
        await bot.send_message(game_to_leave.chat.id, f'👋 ({mention}) - Покинув(ла) гру!')
        await bot.send_message(game_to_leave.chat.id, '🎮 Гра завершена, оскільки не залишилося гравців!')
        await message.answer(f'👋 ({mention}) - Ви успішно покинули гру в іншому чаті, і вона була завершена.')
    else:
        if game_to_leave.started:
            await bot.send_message(game_to_leave.chat.id, f'👋 ({mention}) - Покинув(ла) гру\n🎯 Хід робить гравець {game_to_leave.current_player.mention}')
        else:
            await bot.send_message(game_to_leave.chat.id, f'👋 ({mention}) - Покинув(ла) лобі!')
