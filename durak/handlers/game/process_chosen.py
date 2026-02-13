from aiogram import types

from loader import bot, dp, gm, CHOISE
from durak.objects import *
from durak.logic import actions


async def send_cheat_att(player: Player):
    chat = player.game.chat
    user = player.user
    await bot.send_message(
            chat.id,
            text = f"🚫 Спроба шахраювати {user.get_mention(as_html=True)}"
        )


@dp.chosen_inline_handler()
async def result_handler(query: types.ChosenInlineResult):
    ''' Inline process '''
    user = types.User.get_current()
    player = gm.player_for_user(user)

    if player is None:
        return


    game = player.game
    field_old = game.field
    result_id = query.result_id
    chat = game.chat

    field_cards = set(game.attacking_cards) | set(game.defending_cards)

    if result_id in ('hand', 'gameinfo', 'nogame'):
        return

    result_id, anti_cheat = result_id.split(':')
    split_result_id = result_id.split('-')
    last_anti_cheat = player.anti_cheat
    player.anti_cheat += 1

    current = game.current_player
    opponent = game.opponent_player


    if result_id.startswith('mode_'):
        # First 5 characters are 'mode_', the rest is the gamemode.
        mode = result_id[5:]
        return
    
    elif len(result_id) == 36:  # UUID result
        return
    
    elif int(anti_cheat) != last_anti_cheat:
        # cheat attempt
        await send_cheat_att(player)
        return
    
    elif result_id == 'draw':
        await actions.do_draw(player)

    elif result_id == 'pass':
        await actions.do_pass(player)
    
    elif len(split_result_id) == 1:  # ATK
        try:
            atk_card = c.from_str(split_result_id[0])
        except:
            return
        
        # Special case: defender clicking on attack card to select defense
        if player == game.opponent_player and atk_card in game.attacking_cards and game.field.get(atk_card) is None:
            # This is defender selecting which attack card to defend against
            # Don't process as attack, let the inline query show defense options
            return
        
        # Only current_player (attacker) and support_player can attack
        if player != game.current_player and player != game.support_player:
            await send_cheat_att(player)
            return
        else:
            # Check if this is a valid attack move
            if atk_card not in player.cards:
                await send_cheat_att(player)
                return
            # Check if player can add this card to field
            if not player.can_add_to_field(atk_card):
                await send_cheat_att(player)
                return
            # Additional check: ensure this card hasn't been played already
            if atk_card in field_cards:
                await send_cheat_att(player)
                return
            # Check attack limits based on player type
            if player == game.current_player and not game.allow_atack:
                await send_cheat_att(player)
                return
            if player == game.support_player and not game.allow_support_attack:
                await send_cheat_att(player)
                return
            # opponent.anti_cheat += 1
            await actions.do_attack_card(player, atk_card)

    elif len(split_result_id) == 2:  # DEF
        # Only opponent_player (defender) can defend
        if player != game.opponent_player:
            await send_cheat_att(player)
            return
        try:
            atk_card = c.from_str(split_result_id[0])
            def_card = c.from_str(split_result_id[1])
        except:
            return
        else:
            # Check if this is a valid defense move
            if atk_card not in game.attacking_cards:
                await send_cheat_att(player)
                return
            if game.field.get(atk_card) is not None:
                await send_cheat_att(player)
                return
            if def_card not in player.cards:
                await send_cheat_att(player)
                return
            if not player.can_beat(atk_card, def_card):
                await send_cheat_att(player)
                return
            # Additional check: ensure this card hasn't been played already
            if def_card in field_cards:
                await send_cheat_att(player)
                return
            # current.anti_cheat += 1
            await actions.do_defence_card(player, atk_card, def_card)
    
    else:
        return
    
    try:
        gm.get_game_from_chat(chat)
    except NoGameInChatError:
        return
    else:
        if game.field != field_old or game.current_player != current:
            if game.current_player == current:
                text = (
                    f'✅ <b>Хід залишається!</b>\n\n'
                    f'⚔️ <b>Атакує:</b> {game.current_player.user.get_mention(as_html=True)} 🃏 {len(game.current_player.cards)} карт\n'
                    f'🛡️ <b>Захищається:</b> {game.opponent_player.user.get_mention(as_html=True)} 🃏 {len(game.opponent_player.cards)} карт\n'
                    f'🎯 <b>Козир:</b> {game.deck.trump_ico} | 📦 <b>В колоді:</b> {len(game.deck.cards)} карт'
                )
            else:
                text = (
                    f'🔄 <b>Перехід ходу!</b>\n\n'
                    f'⚔️ <b>Атакує:</b> {game.current_player.user.get_mention(as_html=True)} 🃏 {len(game.current_player.cards)} карт\n'
                    f'🛡️ <b>Захищається:</b> {game.opponent_player.user.get_mention(as_html=True)} 🃏 {len(game.opponent_player.cards)} карт\n'
                    f'🎯 <b>Козир:</b> {game.deck.trump_ico} | 📦 <b>В колоді:</b> {len(game.deck.cards)} карт'
                )

            if query.inline_message_id:
                try:
                    await bot.edit_message_reply_markup(
                        inline_message_id=query.inline_message_id,
                        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=CHOISE),
                    )
                except Exception:
                    await bot.send_message(chat.id, text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=CHOISE))
            else:
                await bot.send_message(chat.id, text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=CHOISE))