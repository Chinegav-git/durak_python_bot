
import asyncio
from aiogram import types, Bot

from loader import gm, CHOISE
from ..db import ChatSetting, UserSetting, session
from ..objects import *
from ..objects import card as c


class NotEnoughPlayersError(Exception):
    """Not enough players to continue the game."""
    pass


async def _delete_message_after_delay(chat_id: int, message_id: int, delay: int):
    """Deletes a message after a specified delay."""
    await asyncio.sleep(delay)
    try:
        bot = Bot.get_current()
        await bot.delete_message(chat_id, message_id)
    except Exception:
        pass


async def send_turn_notification(game: Game):
    """ Sends notification for a normal turn change ("Бито"). """
    bot = Bot.get_current()
    attacker = game.current_player
    defender = game.opponent_player
    if not defender:
        return

    text = (
        f'✅ <b>Перехід ходу</b>\n\n'
        f'⚔️ Атакує: {attacker.user.get_mention(as_html=True)} (🃏{len(attacker.cards)})\n'
        f'🛡️ Захищається: {defender.user.get_mention(as_html=True)} (🃏{len(defender.cards)})\n\n'
        f'🃏 Козир: {game.deck.trump_ico}\n'
        f'🃏 В колоді: {len(game.deck.cards)} карт'
    )
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=CHOISE)
    await bot.send_message(game.chat.id, text, reply_markup=reply_markup)


async def win(game: Game, player: Player):
    chat = game.chat
    bot = Bot.get_current()

    with session:
        user = player.user
        us = UserSetting.get(id=user.id) or UserSetting.create(id=user.id)
        if us.stats:
            us.first_places += 1
    
    if not hasattr(game, 'winners'):
        game.winners = []

    if not game.winner:
        game.winner = player
        await bot.send_message(chat.id, f'🏆 <a href="tg://user?id={player.user.id}">{player.user.full_name}</a> - переможець!')
    else:
        await bot.send_message(chat.id, f'🎉 <a href="tg://user?id={player.user.id}">{player.user.full_name}</a> - теж перемагає!')
    
    if player not in game.winners:
        game.winners.append(player)


async def do_turn(game: Game, skip_def: bool = False):
    chat = game.chat
    
    while True:
        if game.game_is_over:
            if gm.get_game_from_chat(chat):
                winners_text = "\n".join([f'🏆 <a href="tg://user?id={p.user.id}">{p.user.full_name}</a>' for p in getattr(game, 'winners', [])])
                losers_text = "\n".join([f'💔 <a href="tg://user?id={p.user.id}">{p.user.full_name}</a>' for p in game.players])
                gm.end_game(game.chat)
                await Bot.get_current().send_message(
                    chat.id,
                    f'🎮 Гру закінчено!\n\n'
                    f'<b>Переможці:</b>\n{winners_text}\n\n'
                    f'<b>Програвші:</b>\n{losers_text}'
                )
            return

        player_has_left = False
        for player in list(game.players):
            if not player.cards and not player.finished_game:
                await win(game, player)
                player.finished_game = True
                if player in game.players:
                    game.players.remove(player)
                player_has_left = True
                break
        
        if player_has_left:
            continue
        else:
            break

    game.turn(skip_def=skip_def)
    # Only send notification on normal turn change to avoid duplicates
    if not skip_def:
        await send_turn_notification(game)


async def do_leave_player(player: Player, from_turn: bool = False):
    game = player.game
    if not game.started:
        if player in game.players:
            game.players.remove(player)
        return

    with session:
        user = player.user
        us = UserSetting.get(id=user.id) or UserSetting.create(id=user.id)
        if us.stats:
            us.games_played += 1
    
    if not from_turn:
        was_defender = (game.opponent_player and player.user.id == game.opponent_player.user.id)
        if player in game.players:
            game.players.remove(player)
        if len(game.players) < 2:
            raise NotEnoughPlayersError("Not enough players to continue")
        await do_turn(game, skip_def=was_defender)


async def do_pass(player: Player):
    game = player.game
    bot = Bot.get_current()

    if player != game.current_player:
        return

    game.is_pass = True
    
    msg = await bot.send_message(
        game.chat.id,
        f"Пас! {player.user.get_mention(as_html=True)} більше не підкидає в цьому раунді."
    )
    if msg:
        asyncio.create_task(_delete_message_after_delay(msg.chat.id, msg.message_id, 7))

    if game.all_beaten_cards:
        await do_turn(game)


async def do_draw(player: Player):
    game = player.game
    bot = Bot.get_current()

    for msg_id in list(game.attack_announce_message_ids.values()):
        try:
            await bot.delete_message(game.chat.id, msg_id)
        except Exception:
            pass
    game.attack_announce_message_ids.clear()

    for sticker_id in list(game.attack_sticker_message_ids.values()):
        try:
            await bot.delete_message(game.chat.id, sticker_id)
        except Exception:
            pass
    game.attack_sticker_message_ids.clear()
    
    taking_player = game.opponent_player
    game.take_all_field()
    await do_turn(game, skip_def=True) # This updates game state but won't send a message

    # Now, send the specific "take cards" message
    attacker = game.current_player
    defender = game.opponent_player
    
    text = (
        f'↪️ <b>Хід залишається</b>\n\n'
        f'🫳 {taking_player.user.get_mention(as_html=True)} бере карти.\n'
        f'⚔️ Атакує: {attacker.user.get_mention(as_html=True)} (🃏{len(attacker.cards)})\n'
        f'🛡️ Захищається: {defender.user.get_mention(as_html=True)} (🃏{len(defender.cards)})\n\n'
        f'🃏 Козир: {game.deck.trump_ico}\n'
        f'🃏 В колоді: {len(game.deck.cards)} карт'
    )
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=CHOISE)
    await bot.send_message(game.chat.id, text, reply_markup=reply_markup)


async def do_attack_card(player: Player, card: Card):
    game = player.game
    user = player.user
    bot = Bot.get_current()

    if player == game.current_player:
        game.is_pass = False

    player.play_attack(card)
    
    with session:
        cs = ChatSetting.get(id=game.chat.id)
        display_mode = cs.display_mode if cs else 'text'
        us = UserSetting.get(id=user.id) or UserSetting.create(id=user.id)
        if us.stats:
            us.cards_atack += 1
    
    if not player.cards:
        if len(game.players) <= 2 and not game.deck.cards:
            game.is_final = True
            
    beat_markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='⚔️ Побити цю карту!', switch_inline_query_current_chat=f'{repr(card)}')]
    ])

    sticker_msg = None
    if display_mode in ['text_and_sticker', 'sticker_and_button']:
        style = 'trump_normal' if card.suit == game.trump else 'normal'
        sticker_id = c.THEMES[c.ACTIVE_THEME][style].get(repr(card))
        if sticker_id:
            try:
                sticker_msg = await bot.send_sticker(game.chat.id, sticker_id, reply_markup=beat_markup if display_mode == 'sticker_and_button' else None)
                if sticker_msg:
                    game.attack_sticker_message_ids[card] = sticker_msg.message_id
            except Exception:
                pass

    if not (display_mode == 'sticker_and_button' and sticker_msg):
        text = f"⚔️ <b>{user.get_mention(as_html=True)}</b> підкинув(ла) карту: {str(card)}\n🛡️ для {game.opponent_player.user.get_mention(as_html=True)}"
        msg = await bot.send_message(game.chat.id, text, reply_markup=beat_markup)
        if msg:
            game.attack_announce_message_ids[card] = msg.message_id


async def do_defence_card(player: Player, atk_card: Card, def_card: Card):
    game = player.game
    user = player.user
    bot = Bot.get_current()

    player.play_defence(atk_card, def_card)
    
    with session:
        us = UserSetting.get(id=user.id) or UserSetting.create(id=user.id)
        if us.stats:
            us.cards_beaten += 1

    announce_id = game.attack_announce_message_ids.pop(atk_card, None)
    if announce_id:
        asyncio.create_task(_delete_message_after_delay(game.chat.id, announce_id, 7))
    sticker_id = game.attack_sticker_message_ids.pop(atk_card, None)
    if sticker_id:
        asyncio.create_task(_delete_message_after_delay(game.chat.id, sticker_id, 7))

    if game.all_beaten_cards and (game.is_pass or not game.attacker_can_continue):
        await do_turn(game)
    else:
        toss_more_markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text='↪️ Підкинути ще', switch_inline_query_current_chat='')]
        ])
        await bot.send_message(
            game.chat.id,
            f"🛡️ <b>{user.get_mention(as_html=True)}</b> побив(ла) карту {str(atk_card)} картою {str(def_card)}",
            reply_markup=toss_more_markup,
        )
