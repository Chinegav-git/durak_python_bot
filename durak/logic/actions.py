
import asyncio
from contextlib import suppress
from aiogram import types, Bot
from pony.orm import db_session

from loader import gm, CHOISE
from ..db import ChatSetting, UserSetting
from ..objects import Game, Player, Card
from ..objects import card as c

class NotEnoughPlayersError(Exception):
    pass

async def _delete_message_after_delay(chat_id: int, message_id: int, delay: int):
    await asyncio.sleep(delay)
    try:
        await Bot.get_current().delete_message(chat_id, message_id)
    except Exception:
        pass

async def send_turn_notification(game: Game):
    bot = Bot.get_current()
    attacker = game.current_player
    defender = game.opponent_player
    if not defender:
        return

    text = (
        f'✅ <b>Перехід ходу</b>\n\n'
        f'⚔️ Атакує: {attacker.mention} (🃏{len(attacker.cards)})\n'
        f'🛡️ Захищається: {defender.mention} (🃏{len(defender.cards)})\n\n'
        f'🃏 Козир: {game.deck.trump_ico}\n'
        f'🃏 В колоді: {len(game.deck.cards)} карт'
    )
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=CHOISE)
    await bot.send_message(game.id, text, reply_markup=reply_markup)

async def send_no_more_attacks_notification(game: Game):
    bot = Bot.get_current()
    defender = game.opponent_player
    if not defender or not game.round_attackers:
        return

    main_attacker = game.round_attackers[0]
    support_attackers = []
    seen_attackers = {main_attacker.id}
    for player in game.round_attackers[1:]:
        if player.id not in seen_attackers:
            support_attackers.append(player)
            seen_attackers.add(player.id)

    text = f"🛡️ {defender.mention} відбив(ла) усі карти.\n🔄 Більше підкидати не можна.\n\n⚔️ Атакував(ла): {main_attacker.mention}"
    if support_attackers:
        support_mentions = ', '.join([p.mention for p in support_attackers])
        text += f"\n↪️ Підкидував(ли): {support_mentions}"

    msg = await bot.send_message(game.id, text)
    if msg:
        asyncio.create_task(_delete_message_after_delay(msg.chat.id, msg.message_id, 10))

@db_session
def _update_win_stats(user_id: int):
    us = UserSetting.get(id=user_id)
    if us and us.stats:
        us.first_places += 1

async def win(game: Game, player: Player):
    await asyncio.to_thread(_update_win_stats, player.id)
    
    if not hasattr(game, 'winners'):
        game.winners = []

    if player not in game.winners:
        bot = Bot.get_current()
        if not game.winner:
            game.winner = player
            await bot.send_message(game.id, f'🏆 {player.mention} - переможець!')
        else:
            await bot.send_message(game.id, f'🎉 {player.mention} - теж перемагає!')
        game.winners.append(player)
    
    await gm.save_game(game)

async def do_turn(game: Game, skip_def: bool = False):
    while True:
        if game.game_is_over:
            if await gm.get_game_from_chat(game.id):
                final_text = gm.get_game_end_message(game)
                await gm.end_game(game)
                await Bot.get_current().send_message(game.id, final_text, reply_markup=types.ReplyKeyboardRemove())
            return

        player_has_left = False
        for player in list(game.players):
            if not player.cards and not player.finished_game:
                await win(game, player)
                player.finished_game = True
                player_has_left = True

        if player_has_left:
            continue
        else:
            break

    game.turn(skip_def=skip_def)
    await gm.save_game(game)

    if not skip_def:
        await send_turn_notification(game)

@db_session
def _update_leave_stats(user_id: int):
    us = UserSetting.get(id=user_id)
    if us and us.stats:
        us.games_played += 1

async def do_leave_player(game: Game, player: Player, from_turn: bool = False):
    if not game.started:
        if player in game.players:
            game.players.remove(player)
        await gm.save_game(game)
        return

    await asyncio.to_thread(_update_leave_stats, player.id)
    player.leave(game)
    player.finished_game = True

    if not from_turn:
        was_defender = (game.opponent_player and player.id == game.opponent_player.id)
        if len([p for p in game.players if not p.finished_game]) < 2:
            raise NotEnoughPlayersError("Not enough players to continue")
        await do_turn(game, skip_def=was_defender)

async def do_pass(game: Game, player: Player):
    if player != game.current_player:
        return

    game.is_pass = True
    await gm.save_game(game)
    
    bot = Bot.get_current()
    msg = await bot.send_message(game.id, f"Пас! {player.mention} більше не підкидає в цьому раунді.")
    if msg:
        asyncio.create_task(_delete_message_after_delay(msg.chat.id, msg.message_id, 7))

    if game.all_beaten_cards:
        await do_turn(game)

async def do_draw(game: Game, player: Player):
    bot = Bot.get_current()

    for msg_id in list(game.attack_announce_message_ids.values()):
        with suppress(Exception): await bot.delete_message(game.id, msg_id)
    game.attack_announce_message_ids.clear()

    for sticker_id in list(game.attack_sticker_message_ids.values()):
        with suppress(Exception): await bot.delete_message(game.id, sticker_id)
    game.attack_sticker_message_ids.clear()
    
    taking_player = game.opponent_player
    game.take_all_field()
    await do_turn(game, skip_def=True)

    attacker = game.current_player
    defender = game.opponent_player
    
    text = (
        f'↪️ <b>Хід залишається</b>\n\n'
        f'🫳 {taking_player.mention} бере карти.\n'
        f'⚔️ Атакує: {attacker.mention} (🃏{len(attacker.cards)})\n'
        f'🛡️ Захищається: {defender.mention} (🃏{len(defender.cards)})\n\n'
        f'🃏 Козир: {game.deck.trump_ico}\n'
        f'🃏 В колоді: {len(game.deck.cards)} карт'
    )
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=CHOISE)
    await bot.send_message(game.id, text, reply_markup=reply_markup)

@db_session
def _get_attack_settings(chat_id: int, user_id: int):
    cs = ChatSetting.get(id=chat_id)
    us = UserSetting.get(id=user_id)
    if us and us.stats:
        us.cards_atack += 1
    display_mode = cs.display_mode if cs else 'text'
    theme_name = cs.card_theme if cs else 'classic'
    return display_mode, theme_name

async def do_attack_card(game: Game, player: Player, card: Card):
    bot = Bot.get_current()
    display_mode, theme_name = await asyncio.to_thread(_get_attack_settings, game.id, player.id)

    if player == game.current_player:
        game.is_pass = False

    if player not in game.round_attackers:
        game.round_attackers.append(player)

    player.play_attack(game, card)

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
                sticker_msg = await bot.send_sticker(game.id, sticker_id, reply_markup=beat_markup if display_mode == 'sticker_and_button' else None)
                if sticker_msg:
                    game.attack_sticker_message_ids[card] = sticker_msg.message_id
                    await gm.save_game(game)
            except Exception:
                pass

    if not (display_mode == 'sticker_and_button' and sticker_msg):
        text = f"⚔️ <b>{player.mention}</b> підкинув(ла) карту: {str(card)}\n🛡️ для {game.opponent_player.mention}"
        msg = await bot.send_message(game.id, text, reply_markup=beat_markup)
        if msg:
            game.attack_announce_message_ids[card] = msg.message_id
            await gm.save_game(game)

@db_session
def _update_defense_stats(user_id: int):
    us = UserSetting.get(id=user_id)
    if us and us.stats:
        us.cards_beaten += 1

async def do_defence_card(game: Game, player: Player, atk_card: Card, def_card: Card):
    bot = Bot.get_current()

    player.play_defence(game, atk_card, def_card)
    await asyncio.to_thread(_update_defense_stats, player.id)

    announce_id = game.attack_announce_message_ids.pop(atk_card, None)
    if announce_id:
        asyncio.create_task(_delete_message_after_delay(game.id, announce_id, 7))
    sticker_id = game.attack_sticker_message_ids.pop(atk_card, None)
    if sticker_id:
        asyncio.create_task(_delete_message_after_delay(game.id, sticker_id, 7))

    await gm.save_game(game)

    active_players_count = len([p for p in game.players if not p.finished_game])
    should_autopass = (not game.attacker_can_continue) and (active_players_count < 3)

    if game.all_beaten_cards and (game.is_pass or should_autopass):
        await do_turn(game)
    else:
        toss_more_markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text='↪️ Підкинути ще', switch_inline_query_current_chat='')]
        ])
        await bot.send_message(
            game.id,
            f"🛡️ <b>{player.mention}</b> побив(ла) карту {str(atk_card)} картою {str(def_card)}",
            reply_markup=toss_more_markup,
        )
        
        if not game.allow_atack and active_players_count > 2:
            await send_no_more_attacks_notification(game)
