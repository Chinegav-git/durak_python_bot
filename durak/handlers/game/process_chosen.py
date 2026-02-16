from aiogram import types
from typing import Optional

from loader import bot, dp, gm
from durak.objects import * # This will import NoGameInChatError from durak.objects.errors
from durak.logic import actions, result


def get_player_for_user(user: types.User) -> Optional[Player]:
    """Finds the player object for a given user across all active games."""
    for game in gm.games.values():
        for player in game.players:
            if player.user.id == user.id:
                return player
    return None


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
    player = get_player_for_user(user)

    if player is None or not player.game.started:
        return

    game = player.game
    result_id = query.result_id
    chat = game.chat

    if result_id in ('hand', 'gameinfo', 'nogame'):
        return

    # ANTI-CHEAT
    try:
        result_id, anti_cheat = result_id.split(':')
        split_result_id = result_id.split('-')
        last_anti_cheat = player.anti_cheat
        player.anti_cheat += 1
        if int(anti_cheat) != last_anti_cheat:
            # await send_cheat_att(player)
            return # Ignore old queries
    except (ValueError, IndexError):
        await send_cheat_att(player) # Invalid format
        return

    field_cards = set(game.attacking_cards) | set(game.defending_cards)

    if result_id.startswith('mode_'):
        mode = result_id[5:]
        return
    
    elif len(result_id) == 36:  # UUID result, ignore
        return
    
    elif result_id == 'draw':
        await actions.do_draw(player)

    elif result_id == 'pass':
        await actions.do_pass(player)
    
    elif len(split_result_id) == 1:  # ATTACK
        try:
            atk_card_str = split_result_id[0]
            atk_card = next((card for card in player.cards if repr(card) == atk_card_str), None)
            if atk_card is None:
                return
        except Exception:
            return
        
        if player == game.opponent_player and atk_card in game.attacking_cards and game.field.get(atk_card) is None:
            return
        
        if not (player == game.current_player or player == game.support_player):
            return

        if not player.can_add_to_field(atk_card) or \
           (player == game.current_player and not game.allow_atack) or \
           (player == game.support_player and not game.allow_support_attack) or \
           atk_card in field_cards:
            return
            
        await actions.do_attack_card(player, atk_card)

    elif len(split_result_id) == 2:  # DEFEND
        if player != game.opponent_player:
            return
        
        try:
            atk_card_str, def_card_str = split_result_id
            atk_card = next((card for card in game.attacking_cards if repr(card) == atk_card_str), None)
            def_card = next((card for card in player.cards if repr(card) == def_card_str), None)

            if not atk_card or not def_card:
                return
        except Exception:
            return

        if not player.can_beat(atk_card, def_card) or \
           game.field.get(atk_card) is not None or \
           def_card in field_cards:
            return

        await actions.do_defence_card(player, atk_card, def_card)
