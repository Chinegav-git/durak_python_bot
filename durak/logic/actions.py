from ..objects import *
from loader import gm
from ..db import UserSetting, session
from aiogram import types, Bot
import asyncio


async def win(game: Game, player: Player):
    chat = game.chat
    bot = Bot.get_current()

    if not game.winner:
        # First
        # satistic
        with session as s:
            user = player.user
            us = UserSetting.get(id=user.id)
            if not us:
                us = UserSetting(id=user.id)
            if us.stats:
                us.first_places += 1  # first winner
            
        game.winner = player
        await bot.send_message(chat.id, f'🏆 ({player.user.get_mention(as_html=True)}) - Перший переможець!')
    else:    
        await bot.send_message(chat.id, f'🎉 ({player.user.get_mention(as_html=True)}) - Перемагає!')


async def do_turn(game: Game, skip_def: bool = False):
    """errors:
    ...
    """
    chat = game.chat
    bot = Bot.get_current()

    # Check for players with no cards BEFORE rotating attacker.
    for pl in list(game.players):
        if pl.cards:
            continue

        # If game is not in final phase, the first player who ran out wins.
        if not game.is_final:
            await win(game, pl)

            try:
                await do_leave_player(pl, from_turn=True)
            except NotEnoughPlayersError:
                gm.end_game(game.chat)
                await bot.send_message(chat.id, '🎮 Гра завершена!')
                return

            try:
                game = gm.get_game_from_chat(chat)
            except NoGameInChatError:
                await bot.send_message(chat.id, '🎮 Гра завершена!')
                return
        else:
            # Final phase: if both players have no cards -> draw, else current attacker wins.
            # Here `game.current_player` and `game.opponent_player` refer to the
            # attacker/opponent at the moment before turn rotation, which is
            # the correct reference for resolving final-phase results.
            if not game.opponent_player.cards and not game.current_player.cards:
                gm.end_game(game.chat)
                await bot.send_message(chat.id, "🤝 Відбулася нічия :>")
            else:
                await win(game, game.current_player)

            await bot.send_message(chat.id, '🎮 Гра завершена!')
            return

    # Now perform turn rotation and refill hands for next attacker.
    game.turn(skip_def=skip_def)

    
async def do_leave_player(player: Player, from_turn: bool = False):
    """errors:

    - NotEnoughPlayersError
    """
    game = player.game

    if not game.started:
        game.players.remove(player)
        return
    
    try:
        # stats
        with session as s:
            user = player.user
            us = UserSetting.get(id=user.id)
            if not us:
                us = UserSetting(id=user.id)

            if us.stats:
                us.games_played += 1
    except Exception as e:
        import logging
        logging.error(f"[actions] [stat_leave_+] [Error]: {e}")
    
    index = game.players.index(player)

    current = game.current_player
    opponent = game.opponent_player
    attacker_id = game.attacker_index

    if player in [current, opponent]:
        game._clear_field()

    game.players.remove(player)
    if not (player in [current, opponent] or index > attacker_id+1):
        game.attacker_index = (game.attacker_index + 1) % len(game.players)

    if len(game.players) <= 1:
        raise NotEnoughPlayersError
    
    if player in [current, opponent]:
        if not from_turn:
            await do_turn(game)


async def do_pass(player: Player):
    game = player.game
    game.is_pass = True

    if game.all_beaten_cards:
        await do_turn(game)


async def do_draw(player: Player):
    game = player.game
    game.take_all_field()
    await do_turn(game, True)


async def do_attack_card(player: Player, card: Card):
    player.play_attack(card)
    game = player.game
    user = player.user
    bot = Bot.get_current()
    
    # stats
    with session:
        us = UserSetting.get(id=user.id)
        if not us:
            us = UserSetting(id=user.id)
        if us.stats:
            us.cards_played += 1
            us.cards_atack += 1
    
    if not player.cards:
        """ Auto Pass """
        game.is_pass = True

        # play last card in a game
        if len(game.players) <= 2:
            if (not player.cards) and (not game.deck.cards):
                game.is_final = True

    try:
        beat = [[types.InlineKeyboardButton(text='⚔️ Побити цю карту!', switch_inline_query_current_chat=f'{repr(card)}')]]
        msg = await bot.send_message(
            game.chat.id,
            f"⚔️ <b>{user.get_mention(as_html=True)}</b> підкинув(ла) карту: {str(card)}",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=beat),
        )
        game.attack_announce_message_ids[card] = msg.message_id
    except Exception:
        # If the bot has no permission to post buttons / HTML etc., do not break the game flow.
        pass

            
async def do_defence_card(player: Player, atk_card: Card, def_card: Card):
    player.play_defence(atk_card, def_card)
    game = player.game
    user = player.user
    bot = Bot.get_current()
    
    # stats
    with session:
        us = UserSetting.get(id=user.id)
        if not us:
            us = UserSetting(id=user.id)
        
        if us.stats:
            us.cards_played += 1
            us.cards_beaten += 1
    
    if game.all_beaten_cards:
        if game.is_pass:
            await do_turn(game)

    announce_id = game.attack_announce_message_ids.pop(atk_card, None)
    if announce_id:
        async def _delete_later(chat_id: int, message_id: int):
            await asyncio.sleep(7)
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception:
                pass

        asyncio.create_task(_delete_later(game.chat.id, announce_id))

    try:
        await bot.send_message(
            game.chat.id,
            f"🛡️ <b>{user.get_mention(as_html=True)}</b> побив(ла) карту {str(atk_card)} картою {str(def_card)}",
        )
    except Exception:
        pass