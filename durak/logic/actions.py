from aiogram import Bot
from aiogram import types

from durak.logic.game_manager import GameManager
from durak.db.models import ChatSetting, UserSetting
from durak.objects import *
from durak.objects import card as c
from durak.utils.i18n import t


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
        f'⚔️ <b>Атакує:</b> {attacker.user.get_mention(as_html=True)} (🃏{len(attacker.cards)})\n'
        f'🛡️ <b>Захищається:</b> {defender.user.get_mention(as_html=True)} (🃏{len(defender.cards)})\n\n'
        f'🎯 <b>Козир:</b> {game.deck.trump_ico}\n'
        f'📦 <b>В колоді:</b> {len(game.deck.cards)} карт'
    )
    
    # Добавляем отображение карт на столе
    if game.field:
        table_text = ""
        for atk_card, def_card in game.field.items():
            if def_card:
                table_text += f'⚔️ {str(atk_card)} 🛡️ {str(def_card)}\n'
            else:
                table_text += f'⚔️ {str(atk_card)}\n'
        text += table_text
    
    # Создаем клавиатуру только с кнопкой "Мои карты"
    builder = InlineKeyboardBuilder()
    builder.button(text=t('buttons.my_cards'), switch_inline_query_current_chat='')
    
    await bot.send_message(game.chat.id, text, reply_markup=builder.as_markup())


async def send_no_more_attacks_notification(game: Game):
    """
    Sends a notification that no more cards can be thrown in the current round.
    This is used in games with 3 or more players.
    """
    bot = Bot.get_current()
    defender = game.opponent_player
    if not defender:
        return

    # The main attacker is always: first in: list of round attackers
    main_attacker = game.round_attackers[0]
    
    # Other attackers are all subsequent unique players in: list
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


async def win(game: Game, player: Player):
    chat = game.chat
    bot = Bot.get_current()

    user = player.user
    us = await UserSetting.get_or_create(id=user.id)
    if us.stats:
        us.first_places += 1
    
    if not hasattr(game, 'winners'):
        game.winners = []

    if not game.winner:
        game.winner = player
        await bot.send_message(chat.id, f'🏆 {user.get_mention(as_html=True)} - переможець!')
    else:
        await bot.send_message(chat.id, f'🎉 {user.get_mention(as_html=True)} - теж перемагає!')
    
    if player not in game.winners:
        game.winners.append(player)


async def do_turn(game: Game, skip_def: bool = False):
    chat = game.chat
    
    while True:
        if game.game_is_over:
            if gm.get_game_from_chat(chat):
                final_text = gm.get_game_end_message(game)
                gm.end_game(game.chat)
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
            # Immediately re-check if: game is over after a player has won
            if game.game_is_over:
                if gm.get_game_from_chat(chat):
                    final_text = gm.get_game_end_message(game)
                    gm.end_game(game.chat)
                    await Bot.get_current().send_message(chat.id, final_text, reply_markup=types.ReplyKeyboardRemove())
                return
            continue
        else:
            break  # All are present, exit: the loop

        game.turn(skip_def=skip_def)
        if not skip_def:
            await send_turn_notification(game)


async def do_leave_player(player: Player, from_turn: bool = False):
    game = player.game
    if not game.started:
        if player in game.players:
            game.players.remove(player)
        return

    user = player.user
    us = await UserSetting.get_or_create(id=user.id)
    if us.stats:
        us.games_played += 1
    
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


async def do_attack_card(player: Player, card: Card):
    game = player.game
    user = player.user
    bot = Bot.get_current()

    with session:
        cs = ChatSetting.get(id=game.chat.id)
        display_mode = cs.display_mode if cs else 'text'
        theme_name = cs.card_theme if cs else 'classic'
        us = UserSetting.get(id=user.id) or UserSetting.create(id=user.id)
        if us.stats:
            us.cards_attack += 1

    if player == game.current_player:
        game.is_pass = False

    # Add player to: list of attackers for this round
    if player not in game.round_attackers:
        game.round_attackers.append(player)

    player.play_attack(card)

    if not player.cards and len(game.players) <= 2 and not game.deck.cards:
        game.is_final = True

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

    # Get number of players still in: game
    active_players_count = len([p for p in game.players if not p.finished_game])
    # In a 2-player game, the turn automatically ends if: attacker can't add more cards
    should_autopass = (not game.attacker_can_continue) and (active_players_count < 3)

    # If all cards are beaten and: attacker passes or is forced to pass, end: turn
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
        
        # If no more attacks are allowed, send: a notification
        if not game.allow_atack and active_players_count > 2:
            await send_no_more_attacks_notification(game)
