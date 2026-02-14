from ..objects import *
from loader import gm
from ..db import UserSetting, session, ChatSetting
from aiogram import types, Bot
import asyncio


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

    if game.all_beaten_cards:
        await do_turn(game)


async def do_draw(player: Player):
    game = player.game
    bot = Bot.get_current()
    
    # SYNCHRONOUS BLOCK: Get settings from DB.
    display_mode = 'text'
    with session:
        cs = ChatSetting.get(id=game.chat.id)
        if cs:
            display_mode = cs.display_mode

    # ASYNCHRONOUS BLOCK: Now, perform async operations.
    if display_mode in ['text_and_sticker', 'sticker_and_button']:
        for sticker_message_id in game.attack_sticker_message_ids.values():
            try:
                await bot.delete_message(chat_id=game.chat.id, message_id=sticker_message_id)
            except Exception:
                pass

    game.take_all_field()
    await do_turn(game, True)


async def do_attack_card(player: Player, card: Card):
    game = player.game
    user = player.user
    bot = Bot.get_current()

    # First, apply game logic changes
    player.play_attack(card)
    
    # SYNCHRONOUS BLOCK
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
        game.is_pass = True
        if len(game.players) <= 2 and not game.deck.cards:
            game.is_final = True

    # ASYNCHRONOUS BLOCK
    beat_markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='⚔️ Побити цю карту!', switch_inline_query_current_chat=f'{repr(card)}')]
    ])

    sticker_msg = None
    if display_mode in ['text_and_sticker', 'sticker_and_button']:
        sticker_msg = await bot.send_sticker(game.chat.id, card.sticker_id)
        game.attack_sticker_message_ids[card] = sticker_msg.message_id

    text = "​"  # Zero-width space for sticker_and_button mode
    if display_mode in ['text', 'text_and_sticker']:
        text = f"⚔️ <b>{user.get_mention(as_html=True)}</b>\nпідкинув(ла) карту: {str(card)}\n🛡️ для {game.opponent_player.user.get_mention(as_html=True)}"

    msg = await bot.send_message(
        game.chat.id,
        text,
        reply_markup=beat_markup
    )
    game.attack_announce_message_ids[card] = msg.message_id

            
async def do_defence_card(player: Player, atk_card: Card, def_card: Card):
    game = player.game
    user = player.user
    bot = Bot.get_current()

    # First, apply game logic changes
    player.play_defence(atk_card, def_card)
    
    # SYNCHRONOUS BLOCK
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
            us.cards_beaten += 1
    
    # --- ASYNCHRONOUS BLOCK ---
    # Check for turn end conditions first
    if (game.all_beaten_cards and len(game.players) == 2 and not game.attacker_can_continue) or \
       (game.all_beaten_cards and game.is_pass):
        await do_turn(game)
        return

    # Clean up messages from the attack phase
    announce_id = game.attack_announce_message_ids.pop(atk_card, None)
    if display_mode in ['text_and_sticker', 'sticker_and_button']:
        sticker_id = game.attack_sticker_message_ids.pop(atk_card, None)
        if sticker_id:
            try:
                await bot.delete_message(chat_id=game.chat.id, message_id=sticker_id)
            except Exception:
                pass

    if announce_id:
        # Schedule deletion of the original attack message
        async def _delete_later(chat_id: int, message_id: int):
            await asyncio.sleep(7)
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception:
                pass
        asyncio.create_task(_delete_later(game.chat.id, announce_id))

    # Send confirmation message
    toss_more_markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='↪️ Підкинути ще', switch_inline_query_current_chat='')]
    ])
    await bot.send_message(
        game.chat.id,
        f"🛡️ <b>{user.get_mention(as_html=True)}</b> побив(ла) карту {str(atk_card)} картою {str(def_card)}",
        reply_markup=toss_more_markup,
    )
