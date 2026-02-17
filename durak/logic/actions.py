
import asyncio
from aiogram import types, Bot

from loader import gm, CHOISE
from ..db import ChatSetting, UserSetting
from ..objects import *
from ..objects import card as c
from pony.orm import db_session

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
    """ Sends notification for a normal turn change ('Бито'). """
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


async def send_no_more_attacks_notification(game: Game):
    """
    Sends a notification that no more cards can be thrown in the current round.
    This is used in games with 3 or more players.
    """
    bot = Bot.get_current()
    defender = game.opponent_player
    if not defender:
        return

    # The main attacker is always the first in the list of round attackers
    main_attacker = game.round_attackers[0]
    
    # Other attackers are all subsequent unique players in the list
    support_attackers = []
    seen_attackers = set()
    for player in game.round_attackers[1:]:
        if player.user.id not in seen_attackers:
            support_attackers.append(player)
            seen_attackers.add(player.user.id)

    text = (
        f"🛡️ {defender.user.get_mention(as_html=True)} відбив(ла) усі карти.\n"
        f"🔄 Більше підкидати не можна.\n\n"
        f"⚔️ Атакував(ла): {main_attacker.user.get_mention(as_html=True)}"
    )

    if support_attackers:
        support_mentions = ', '.join([p.user.get_mention(as_html=True) for p in support_attackers])
        text += f"\n↪️ Підкидував(ли): {support_mentions}"

    msg = await bot.send_message(game.chat.id, text)
    if msg:
        asyncio.create_task(_delete_message_after_delay(msg.chat.id, msg.message_id, 10))


@db_session
def _win_db_session(player: Player):
    user = player.user
    us = UserSetting.get(id=user.id) or UserSetting.create(id=user.id)
    if us.stats:
        us.first_places += 1

async def win(game: Game, player: Player):
    chat = game.chat
    bot = Bot.get_current()

    await asyncio.to_thread(_win_db_session, player)
    
    if not hasattr(game, 'winners'):
        game.winners = []

    if not game.winner:
        game.winner = player
        await bot.send_message(chat.id, f'🏆 {player.user.get_mention(as_html=True)} - переможець!')
    else:
        await bot.send_message(chat.id, f'🎉 {player.user.get_mention(as_html=True)} - теж перемагає!')
    
    if player not in game.winners:
        game.winners.append(player)
    
    await gm.save_game(game)

async def do_turn(game: Game, skip_def: bool = False):
    chat = game.chat
    
    while True:
        if game.game_is_over:
            if await gm.get_game_from_chat(chat):
                final_text = gm.get_game_end_message(game)
                await gm.end_game(game.chat)
                await Bot.get_current().send_message(chat.id, final_text, reply_markup=types.ReplyKeyboardRemove())
            return

        player_has_left = False
        active_players = [p for p in game.players if not p.finished_game]
        
        if len(active_players) > 1:
            for player in list(game.players):
                if not player.cards and not player.finished_game:
                    await win(game, player)
                    player.finished_game = True
                    player_has_left = True

        if player_has_left:
            # Immediately re-check if the game is over after a player has won
            if game.game_is_over:
                if await gm.get_game_from_chat(chat):
                    final_text = gm.get_game_end_message(game)
                    await gm.end_game(game.chat)
                    await Bot.get_current().send_message(chat.id, final_text, reply_markup=types.ReplyKeyboardRemove())
                return
            continue
        else:
            break

    game.turn(skip_def=skip_def)
    await gm.save_game(game)

    if not skip_def:
        await send_turn_notification(game)

@db_session
def _leave_player_db_session(player: Player):
    user = player.user
    us = UserSetting.get(id=user.id) or UserSetting.create(id=user.id)
    if us.stats:
        us.games_played += 1

async def do_leave_player(player: Player, from_turn: bool = False):
    game = player.game
    if not game.started:
        if player in game.players:
            game.players.remove(player)
        await gm.save_game(game)
        return

    await asyncio.to_thread(_leave_player_db_session, player)
    
    if not from_turn:
        was_defender = (game.opponent_player and player.user.id == game.opponent_player.user.id)
        player.finished_game = True
        if len([p for p in game.players if not p.finished_game]) < 2:
            raise NotEnoughPlayersError("Not enough players to continue")
        await do_turn(game, skip_def=was_defender)

async def do_pass(player: Player):
    game = player.game
    bot = Bot.get_current()

    if player != game.current_player:
        return

    game.is_pass = True
    await gm.save_game(game)
    
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
    await do_turn(game, skip_def=True)

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

@db_session
def _attack_card_db_session(game: Game, player: Player):
    cs = ChatSetting.get(id=game.chat.id)
    display_mode = cs.display_mode if cs else 'text'
    theme_name = cs.card_theme if cs else 'classic'
    us = UserSetting.get(id=player.user.id) or UserSetting.create(id=player.user.id)
    if us.stats:
        us.cards_atack += 1
    return display_mode, theme_name

async def do_attack_card(player: Player, card: Card):
    game = player.game
    user = player.user
    bot = Bot.get_current()

    display_mode, theme_name = await asyncio.to_thread(_attack_card_db_session, game, player)

    if player == game.current_player:
        game.is_pass = False

    # Add player to the list of attackers for this round
    if player not in game.round_attackers:
        game.round_attackers.append(player)

    player.play_attack(card)

    if not player.cards and len(game.players) <= 2 and not game.deck.cards:
        game.is_final = True

    await gm.save_game(game)

    beat_markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='⚔️ Побити цю карту!', switch_inline_query_current_chat=f'{repr(card)}')]
    ])

    sticker_msg = None
    if display_mode in ['text_and_sticker', 'sticker_and_button']:
        style = 'trump_normal' if card.suit == game.trump else 'normal'
        sticker_id = c.get_sticker_id(repr(card), theme_name=theme_name, style=style)
        if sticker_id:
            try:
                sticker_msg = await bot.send_sticker(game.chat.id, sticker_id, reply_markup=beat_markup if display_mode == 'sticker_and_button' else None)
                if sticker_msg:
                    game.attack_sticker_message_ids[card] = sticker_msg.message_id
                    await gm.save_game(game)
            except Exception:
                pass

    if not (display_mode == 'sticker_and_button' and sticker_msg):
        text = f"⚔️ <b>{user.get_mention(as_html=True)}</b> підкинув(ла) карту: {str(card)}\n🛡️ для {game.opponent_player.user.get_mention(as_html=True)}"
        msg = await bot.send_message(game.chat.id, text, reply_markup=beat_markup)
        if msg:
            game.attack_announce_message_ids[card] = msg.message_id
            await gm.save_game(game)

@db_session
def _defence_card_db_session(player: Player):
    us = UserSetting.get(id=player.user.id) or UserSetting.create(id=player.user.id)
    if us.stats:
        us.cards_beaten += 1

async def do_defence_card(player: Player, atk_card: Card, def_card: Card):
    game = player.game
    user = player.user
    bot = Bot.get_current()

    player.play_defence(atk_card, def_card)
    
    await asyncio.to_thread(_defence_card_db_session, player)

    announce_id = game.attack_announce_message_ids.pop(atk_card, None)
    if announce_id:
        asyncio.create_task(_delete_message_after_delay(game.chat.id, announce_id, 7))
    sticker_id = game.attack_sticker_message_ids.pop(atk_card, None)
    if sticker_id:
        asyncio.create_task(_delete_message_after_delay(game.chat.id, sticker_id, 7))

    await gm.save_game(game)

    # Get the number of players still in the game
    active_players_count = len([p for p in game.players if not p.finished_game])
    # In a 2-player game, the turn automatically ends if the attacker can't add more cards
    should_autopass = (not game.attacker_can_continue) and (active_players_count < 3)

    # If all cards are beaten and the attacker passes or is forced to pass, end the turn
    if game.all_beaten_cards and (game.is_pass or should_autopass):
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
        
        # If no more attacks are allowed, send a notification
        if not game.allow_atack and active_players_count > 2:
            await send_no_more_attacks_notification(game)

