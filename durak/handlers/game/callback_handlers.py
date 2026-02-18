from contextlib import suppress
from typing import Optional, Tuple
from aiogram import types
from aiogram.utils.exceptions import MessageNotModified, CantParseEntities
from loader import bot, dp, gm
from durak.objects import Game, Player, NoGameInChatError
from durak.logic import actions as a

# Helper function to find player and game, adapted from process_chosen.py
async def get_player_and_game_for_user(user: types.User) -> Tuple[Optional[Player], Optional[Game]]:
    game_keys = await gm.redis.keys("game:*")
    for key in game_keys:
        try:
            chat_id = int(key.decode().split(":", 1)[1])
            game = await gm.get_game_from_chat(chat_id)
            if game:
                player = game.player_for_id(user.id)
                if player:
                    return player, game
        except (NoGameInChatError, IndexError, ValueError):
            continue
    return None, None

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
    try:
        user_id_to_kick = int(callback_query.data.split('|')[1])
    except (IndexError, ValueError):
        await bot.answer_callback_query(callback_query.id, 'Помилка: Неправильний формат даних для кіка.')
        return

    user = callback_query.from_user
    player, game = await get_player_and_game_for_user(user)

    if not player or not game:
        await bot.answer_callback_query(callback_query.id, 'Не вдалося знайти вашу гру!')
        return

    if user.id != game.creator_id:
        await bot.answer_callback_query(callback_query.id, 'Натискати може тільки творець гри!')
        return

    player_to_kick = game.player_for_id(user_id_to_kick)
    if not player_to_kick:
        await bot.answer_callback_query(callback_query.id, 'Гравець не знайдений в цьому лобі!')
        return

    # Use the action from durak.logic to handle leaving
    await a.do_leave_player(game, player_to_kick)

    # After kicking, refresh the player list in the message
    players_list = '\n'.join([
        f'{i+1}. {p.mention}'
        for i, p in enumerate(game.players)
    ])
    
    try:
        with suppress(MessageNotModified, CantParseEntities):
            await bot.edit_message_text(
                inline_message_id=callback_query.inline_message_id,
                text=f'<b>Гравці:</b>\n{players_list}' if game.players else '<b>Гравців більше немає.</b>'
            )
    except Exception as e:
        # Log this error, as editing might fail if the message is too old
        print(f"Error updating kick message: {e}")

