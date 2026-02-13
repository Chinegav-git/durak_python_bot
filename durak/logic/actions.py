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
        await bot.send_message(chat.id, f'🏆 ({player.user.get_mention(as_html=True)}) - переможець!')
    else:    
        await bot.send_message(chat.id, f'🎉 ({player.user.get_mention(as_html=True)}) - теж перемагає!')
    game.winners.append(player)


async def do_turn(game: Game, skip_def: bool = False):
    """
    Handles the turn transition, checks for winners, and ends the game if necessary.
    This function is the heart of the game flow control.
    """
    chat = game.chat
    bot = Bot.get_current()

    # A loop is used to re-evaluate the game state from the beginning
    # whenever a player leaves the game. This simplifies the logic by
    # ensuring checks are always run against the current list of players.
    while True:
        # Pre-check: If only one player remains for any reason, the game is over.
        if len(game.players) <= 1:
            # The game might have already been ended by a previous call that led here.
            # Checking if the game is still in the manager prevents double-ending.
            if gm.get_game_from_chat(chat):
                gm.end_game(game.chat)
                winners_text = "\n".join([f'🏆 {p.user.get_mention(as_html=True)}' for p in game.winners])
                losers_text = "\n".join([f'💔 {p.user.get_mention(as_html=True)}' for p in game.players])
                await bot.send_message(
                    chat.id,
                    f'🎮 Гру закінчено!\n\n'
                    f'<b>Переможці:</b>\n{winners_text}\n\n'
                    f'<b>Програвші:</b>\n{losers_text}'
                )

            return

        player_has_left = False
        for player in list(game.players):
            # A player wins if they have no cards left and the game is not in the final attack.
            if not player.cards:
                if not game.is_final:
                    await win(game, player)
                    try:
                        # The player is removed from the game.
                        await do_leave_player(player, from_turn=True)
                        player_has_left = True
                        # Break the inner 'for' loop to restart the 'while' loop
                        # with the updated player list.
                        break
                    except NotEnoughPlayersError:
                        # This exception means only one player is left after leaving.
                        if gm.get_game_from_chat(chat):
                            gm.end_game(game.chat)
                            winners_text = "\n".join([f'🏆 {p.user.get_mention(as_html=True)}' for p in game.winners])
                            losers_text = "\n".join([f'💔 {p.user.get_mention(as_html=True)}' for p in game.players])
                            await bot.send_message(
                                chat.id,
                                f'🎮 Гру закінчено!\n\n'
                                f'<b>Переможці:</b>\n{winners_text}\n\n'
                                f'<b>Програвші:</b>\n{losers_text}'
                            )
                        return
                else:
                    # FINAL PHASE LOGIC
                    # This block executes when the attacker plays their last card and
                    # the deck is empty.
                    if not game.opponent_player.cards and not game.current_player.cards:
                        # If the defender also has no cards, it's a draw.
                        await bot.send_message(chat.id, "🤝 Нічия")
                    else:
                        # Otherwise, the attacker (current_player) is the winner.
                        await win(game, game.current_player)

                    # End the game regardless of draw or win.
                    if gm.get_game_from_chat(chat):
                        gm.end_game(game.chat)
                        winners_text = "\n".join([f'🏆 {p.user.get_mention(as_html=True)}' for p in game.winners])
                        losers_text = "\n".join([f'💔 {p.user.get_mention(as_html=True)}' for p in game.players])
                        await bot.send_message(
                            chat.id,
                            f'🎮 Гру закінчено!\n\n'
                            f'<b>Переможці:</b>\n{winners_text}\n\n'
                            f'<b>Програвші:</b>\n{losers_text}'
                        )
                    return

        # If a player left, restart the 'while' loop to re-evaluate the new game state.
        if player_has_left:
            continue
        # If the 'for' loop completed without any player leaving, it means it's a normal turn.
        # We can break the 'while' loop and proceed to the next turn.
        else:
            break

    # If the game hasn't ended, proceed with the normal turn rotation.
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
    bot = Bot.get_current()
    
    game.is_pass = True
    msg = await bot.send_message(
        game.chat.id,
        f"Пас! {player.user.get_mention(as_html=True)} більше не підкидає."
    )

    async def _delete_later(chat_id: int, message_id: int):
        await asyncio.sleep(5)
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            pass

    asyncio.create_task(_delete_later(msg.chat.id, msg.message_id))

    # Якщо всі карти вже побиті, коли гравець пасує, передаємо хід
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
            f"⚔️ <b>{user.get_mention(as_html=True)}</b>\nпідкинув(ла) карту: {str(card)}\n🛡️ для {game.opponent_player.user.get_mention(as_html=True)}",
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
    
    # Ключова зміна: перевіряємо пас ТІЛЬКИ ПІСЛЯ того, як всі карти побиті
    if game.all_beaten_cards and game.is_pass:
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
