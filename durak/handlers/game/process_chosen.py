from aiogram import types
from typing import Optional, Tuple

from loader import bot, dp, gm
from durak.objects import Game, Player, NoGameInChatError
from durak.logic import actions

async def get_player_and_game_for_user(user: types.User) -> Tuple[Optional[Player], Optional[Game]]:
    """Finds the player and their game object for a given user across all active games."""
    # This is an assumption based on how GameManager might work with Redis.
    # A more efficient implementation would be a user_id -> game_id mapping in Redis.
    game_keys = await gm.redis.keys("game:*")
    for key in game_keys:
        try:
            chat_id = int(key.decode().split(":", 1)[1])
            game = await gm.get_game_from_chat(chat_id)
            if game:
                player = game.player_for_id(user.id)
                if player:
                    return player, game
        except (NoGameInChatError, IndexError, ValueError):
            continue
    return None, None

async def send_cheat_att(game: Game, player: Player):
    await bot.send_message(
        game.id,
        text=f"🚫 Спроба шахраювати {player.mention}"
    )

@dp.chosen_inline_handler()
async def result_handler(query: types.ChosenInlineResult):
    """ Inline process """ 
    user = query.from_user
    player, game = await get_player_and_game_for_user(user)

    if player is None or game is None or not game.started:
        return

    result_id = query.result_id

    if result_id in ('hand', 'gameinfo', 'nogame'):
        return

    # ANTI-CHEAT
    try:
        result_id, anti_cheat = result_id.split(':')
        split_result_id = result_id.split('-')
        last_anti_cheat = player.anti_cheat
        
        # Increment anti-cheat and save immediately to prevent race conditions
        player.anti_cheat += 1
        await gm.save_game(game)

        if int(anti_cheat) != last_anti_cheat:
            return  # Ignore old queries
    except (ValueError, IndexError):
        await send_cheat_att(game, player)  # Invalid format
        return

    field_cards = set(game.attacking_cards) | set(game.defending_cards)

    if result_id.startswith('mode_'):
        # mode = result_id[5:] # This logic seems incomplete, ignoring for now
        return
    
    elif len(result_id) == 36:  # UUID result, ignore
        return
    
    elif result_id == 'draw':
        await actions.do_draw(game, player)

    elif result_id == 'pass':
        await actions.do_pass(game, player)
    
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

        if not player.can_add_to_field(game, atk_card) or \
           (player == game.current_player and not game.allow_atack) or \
           (player == game.support_player and not game.allow_support_attack) or \
           atk_card in field_cards:
            return
            
        await actions.do_attack_card(game, player, atk_card)

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

        if not player.can_beat(game, atk_card, def_card) or \
           game.field.get(atk_card) is not None or \
           def_card in field_cards:
            return

        await actions.do_defence_card(game, player, atk_card, def_card)
