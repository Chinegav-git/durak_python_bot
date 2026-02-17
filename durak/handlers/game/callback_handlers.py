from contextlib import suppress
from typing import Optional
from aiogram import types
from aiogram.utils.exceptions import MessageNotModified, CantParseEntities
from loader import bot, dp, gm, Commands
from durak.objects import *
from durak.objects.errors import PlayerNotFoundError
from durak.logic import actions as a

async def get_player_for_user(user: types.User) -> Optional[Player]:
    """Finds the player object for a given user across all active games."""
    for game_id in await gm.get_all_games():
        game = await gm.get_game(game_id)
        if not game:
            continue
        for player in game.players:
            if player.user.id == user.id:
                return player
    return None


@dp.callback_query_handler(lambda c: c.data and c.data == 'close')
async def process_callback_close(callback_query: types.CallbackQuery):
    with suppress(MessageNotModified):
        await bot.edit_message_text(
            inline_message_id=callback_query.inline_message_id,
            text='Лобі закрито.'
        )


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('kick'))
async def process_callback_kick(callback_query: types.CallbackQuery):
    """ Kicking a player from a lobby """
    user_id = int(callback_query.data.split('|')[1])
    user = callback_query.from_user
    
    # Assuming the inline_message_id is available and linked to a chat_id
    # This part is tricky as inline queries don't have a direct chat context
    # A potential solution is to encode chat_id in the callback_data, but that's not done here
    # For now, we'll rely on finding the game through the user
    player = await get_player_for_user(user)
    if not player:
        await bot.answer_callback_query(callback_query.id, 'Не вдалося знайти вашу гру!')
        return

    game = player.game

    if user.id != game.creator.id:
        await bot.answer_callback_query(callback_query.id, 'Натискати може тільки творець гри!')
        return

    try:
        player_to_kick = game.player_for_id(user_id)
        if not player_to_kick:
            raise PlayerNotFoundError

        await a.do_leave_player(player_to_kick)

    except PlayerNotFoundError:
        await bot.answer_callback_query(callback_query.id, 'Гравець не знайдений!')
        return

    players_list = '\n'.join([
        f'{i+1}. {player.user.get_mention(as_html=True)}'
        for i, player in enumerate(game.players)
    ])
    with suppress(MessageNotModified, CantParseEntities):
        await bot.edit_message_text(
            inline_message_id=callback_query.inline_message_id,
            text=f'<b>Гравці:</b>\n{players_list}'
        )
