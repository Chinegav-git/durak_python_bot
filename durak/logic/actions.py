
from ..objects import *
from loader import gm
from ..db import UserSetting, session, ChatSetting
from aiogram import types, Bot
import asyncio
from ..objects import card as c


class NotEnoughPlayersError(Exception):
    """Not enough players to continue the game."""
    pass


async def _delete_message_after_delay(chat_id: int, message_id: int, delay: int):
    """Coroutine to delete a message after a specified delay."""
    await asyncio.sleep(delay)
    try:
        bot = Bot.get_current()
        await bot.delete_message(chat_id, message_id)
    except Exception:
        # Ignore exceptions if the message is already deleted or not found
        pass


async def win(game: Game, player: Player):
    chat = game.chat
    bot = Bot.get_current()
    
    # SYNCHRONOUS BLOCK: Perform all database operations first.
    with session:
        user = player.user
        # Use get_or_create pattern
        us = UserSetting.get(id=user.id)
        if not us:
            us = UserSetting(id=user.id)
        if us.stats:
            us.first_places += 1  # first winner

    # ASYNCHRONOUS BLOCK: Now, perform async operations.
    if not game.winner:
        game.winner = player
        await bot.send_message(chat.id, f'🏆 <a href="tg://user?id={player.user.id}">{player.user.full_name}</a> - переможець!')
    else:    
        await bot.send_message(chat.id, f'🎉 <a href="tg://user?id={player.user.id}">{player.user.full_name}</a> - теж перемагає!')
    game.winners.append(player)


async def do_turn(game: Game, skip_def: bool = False):
    # Clean up temporary state at the end of a turn
    if hasattr(game, '_temp_passed_attackers'):
        del game._temp_passed_attackers

    chat = game.chat
    bot = Bot.get_current()

    while True:
        if len(game.players) <= 1:
            if gm.get_game_from_chat(chat):
                winners_text = "\n".join([f'🏆 <a href="tg://user?id={p.user.id}">{p.user.full_name}</a>' for p in game.winners])
                losers_text = "\n".join([f'💔 <a href="tg://user?id={p.user.id}">{p.user.full_name}</a>' for p in game.players])
                gm.end_game(game.chat)
                await bot.send_message(
                    chat.id,
                    f'🎮 Гру закінчено!\n\n'
                    f'<b>Переможці:</b>\n{winners_text}\n\n'
                    f'<b>Програвші:</b>\n{losers_text}'
                )
            return

        player_has_left = False
        for player in list(game.players):
            if not player.cards:
                if not game.is_final:
                    await win(game, player)
                    try:
                        await do_leave_player(player, from_turn=True)
                        player_has_left = True
                        break
                    except NotEnoughPlayersError:
                        if gm.get_game_from_chat(chat):
                            winners_text = "\n".join([f'🏆 <a href="tg://user?id={p.user.id}">{p.user.full_name}</a>' for p in game.winners])
                            losers_text = "\n".join([f'💔 <a href="tg://user?id={p.user.id}">{p.user.full_name}</a>' for p in game.players])
                            gm.end_game(game.chat)
                            await bot.send_message(
                                chat.id,
                                f'🎮 Гру закінчено!\n\n'
                                f'<b>Переможці:</b>\n{winners_text}\n\n'
                                f'<b>Програвші:</b>\n{losers_text}'
                            )
                        return
                else:
                    if not game.opponent_player.cards and not game.current_player.cards:
                        await bot.send_message(chat.id, "🤝 Нічия")
                    else:
                        await win(game, game.current_player)

                    if gm.get_game_from_chat(chat):
                        winners_text = "\n".join([f'🏆 <a href="tg://user?id={p.user.id}">{p.user.full_name}</a>' for p in game.winners])
                        losers_text = "\n".join([f'💔 <a href="tg://user?id={p.user.id}">{p.user.full_name}</a>' for p in game.players])
                        gm.end_game(game.chat)
                        await bot.send_message(
                            chat.id,
                            f'🎮 Гру закінчено!\n\n'
                            f'<b>Переможці:</b>\n{winners_text}\n\n'
                            f'<b>Програвші:</b>\n{losers_text}'
                        )
                    return

        if player_has_left:
            continue
        else:
            break

    game.turn(skip_def=skip_def)
    

async def do_leave_player(player: Player, from_turn: bool = False):
    game = player.game

    if not game.started:
        game.players.remove(player)
        return
    
    # SYNCHRONOUS BLOCK
    with session:
        user = player.user
        us = UserSetting.get(id=user.id)
        if not us:
            us = UserSetting(id=user.id)
        if us.stats:
            us.games_played += 1
    
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
    
    # ASYNCHRONOUS BLOCK
    if player in [current, opponent] and not from_turn:
        await do_turn(game)


async def do_pass(player: Player):
    game = player.game
    
    if not hasattr(game, '_temp_passed_attackers'):
        game._temp_passed_attackers = set()
    
    game._temp_passed_attackers.add(player.user.id)
    
    # Pass is now silent. The decision to end the turn is centralized 
    # in do_defence_card after checking all attackers' statuses.


async def do_draw(player: Player):
    game = player.game
    bot = Bot.get_current()

    # Clean up all attack messages as the turn is forfeit
    for msg_id in getattr(game, 'attack_announce_message_ids', {}).values():
        try:
            await bot.delete_message(game.chat.id, msg_id)
        except Exception:
            pass
    game.attack_announce_message_ids = {}

    for sticker_id in getattr(game, 'attack_sticker_message_ids', {}).values():
        try:
            await bot.delete_message(game.chat.id, sticker_id)
        except Exception:
            pass
    game.attack_sticker_message_ids = {}

    game.take_all_field()
    await do_turn(game, True)


async def do_attack_card(player: Player, card: Card):
    game = player.game
    user = player.user
    bot = Bot.get_current()

    if not hasattr(game, '_temp_passed_attackers'):
        game._temp_passed_attackers = set()

    if player.user.id in getattr(game, '_temp_passed_attackers', set()):
        return

    player.play_attack(card)
    
    display_mode = 'text'
    with session:
        cs = ChatSetting.get(id=game.chat.id)
        if cs:
            display_mode = cs.display_mode

        us = UserSetting.get(id=user.id)
        if not us:
            us = UserSetting(id=user.id)
        if us.stats:
            us.cards_played += 1
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

    text = "​"  # Zero-width space
    if display_mode == 'text' or display_mode == 'text_and_sticker' or (display_mode == 'sticker_and_button' and not sticker_msg):
        text = f"⚔️ <b>{user.get_mention(as_html=True)}</b>\nпідкинув(ла) карту: {str(card)}\n🛡️ для {game.opponent_player.user.get_mention(as_html=True)}"

    msg = None
    if not (display_mode == 'sticker_and_button' and sticker_msg):
        msg = await bot.send_message(
            game.chat.id,
            text,
            reply_markup=beat_markup
        )
        if msg:
            game.attack_announce_message_ids[card] = msg.message_id

            
async def do_defence_card(player: Player, atk_card: Card, def_card: Card):
    game = player.game
    user = player.user
    bot = Bot.get_current()

    player.play_defence(atk_card, def_card)
    
    with session:
        cs = ChatSetting.get(id=game.chat.id)
        display_mode = cs.display_mode if cs else 'text'

        us = UserSetting.get(id=user.id)
        if not us:
            us = UserSetting(id=user.id)
        if us.stats:
            us.cards_played += 1
            us.cards_beaten += 1

    # --- DELAYED MESSAGE CLEANUP ---
    # Schedule the deletion of the attack announcement message after a delay.
    announce_id = game.attack_announce_message_ids.pop(atk_card, None)
    if announce_id:
        asyncio.create_task(_delete_message_after_delay(game.chat.id, announce_id, 7))

    if display_mode in ['text_and_sticker', 'sticker_and_button']:
        sticker_id = game.attack_sticker_message_ids.pop(atk_card, None)
        if sticker_id:
            asyncio.create_task(_delete_message_after_delay(game.chat.id, sticker_id, 7))

    # --- TURN END LOGIC ---
    if game.all_beaten_cards:
        all_attackers_done = True
        passed_attackers = getattr(game, '_temp_passed_attackers', set())
        for p in game.attackers:
            if p.user.id not in passed_attackers and p.can_add_to_field:
                all_attackers_done = False
                break
        
        if all_attackers_done:
            await bot.send_message(game.chat.id, "✅ Бито!")
            await do_turn(game)
            return

    # If the turn is not over, send a confirmation of the defence
    toss_more_markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='↪️ Підкинути ще', switch_inline_query_current_chat='')]
    ])
    await bot.send_message(
        game.chat.id,
        f"🛡️ <b>{user.get_mention(as_html=True)}</b> побив(ла) карту {str(atk_card)} картою {str(def_card)}",
        reply_markup=toss_more_markup,
    )

