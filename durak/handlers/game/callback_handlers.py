from contextlib import suppress
from aiogram import types
from aiogram.utils.exceptions import MessageNotModified, CantParseEntities
from loader import bot, dp, gm, Commands
from durak.objects import *


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
    user = types.User.get_current()
    chat = types.Chat.get_current()

    try:
        game = gm.get_game_from_chat(chat)
    except NoGameInChatError: # FIX
        with suppress(MessageNotModified):
            await bot.edit_message_text(
                inline_message_id=callback_query.inline_message_id,
                text=f'🚫 У цьому чаті немає гри!\n🎮 Створіть її за допомогою - /{Commands.NEW}'
            )
        return

    if user.id != game.creator.id:
        await bot.answer_callback_query(callback_query.id, 'Натискати може тільки творець гри!')
        return
    
    try:
        gm.kick_player(game, user_id)
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


@dp.inline_handler()
async def inline_handler(inline_query: types.InlineQuery):
    """ Main game handler """
    user = types.User.get_current()
    
    try:
        player = gm.get_player_from_user(user)
        game = player.game
    except NoGameInChatError:
        await bot.answer_inline_query(
            inline_query.id,
            [],
            switch_pm_text='У вас немає активних ігор!',
            switch_pm_parameter='start',
            cache_time=0
        )
        return
    except PlayerNotFoundError:
        await bot.answer_inline_query(
            inline_query.id,
            [],
            switch_pm_text=f'Ви не перебуваєте в грі! Приєднатися - /{Commands.JOIN}',
            switch_pm_parameter='join',
            cache_time=0
        )
        return
    except AlreadyJoinedInGlobalError as e:
        await bot.answer_inline_query(
            inline_query.id,
            [],
            switch_pm_text=f'Ви граєте в іншому чаті! Покинути - /{Commands.GLEAVE}',
            switch_pm_parameter='gleave',
            cache_time=0
        )
        return
    
    # player and game
    player = gm.get_player_from_user(user)
    game = player.game
    query = inline_query.query

    if query == '?':
        return await bot.answer_inline_query(
            inline_query.id, [player.game_status_as_inline_article()], cache_time=0
        )

    if not game.started:
        await bot.answer_inline_query(
            inline_query.id,
            [],
            switch_pm_text="Гра ще не почалася!",
            switch_pm_parameter='start',
            cache_time=0
        )
        return

    if game.current_player != player and game.opponent_player != player:
        await bot.answer_inline_query(
            inline_query.id, [player.game_status_as_inline_article()],
            switch_pm_text="Зараз не ваша черга!",
            switch_pm_parameter='start', cache_time=0
        )
        return

    # is current
    if game.current_player == player:
        await bot.answer_inline_query(
            inline_query.id,
            player.get_attack_as_inline_query(query),
            cache_time=0
        )
    # is opponent
    elif game.opponent_player == player:
        await bot.answer_inline_query(
            inline_query.id,
            player.get_defence_as_inline_query(query),
            cache_time=0
        )
