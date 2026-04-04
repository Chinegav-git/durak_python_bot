from aiogram import types
from typing import List, Optional
import asyncio

from loader import bot, dp, gm, CHOISE, db_session
from durak.objects import *
from durak.logic import result as r
from durak.db.chat_settings import get_chat_settings

def get_player_for_user(user: types.User) -> Optional[Player]:
    """Finds the player object for a given user across all active games."""
    for game in gm.games.values():
        for player in game.players:
            if player.user.id == user.id:
                return player
    return None


@dp.inline_handler()
async def inline_handler(query: types.InlineQuery):
    """ Inline handler :> """
    user = types.User.get_current()
    text = query.query or ''
    player = get_player_for_user(user)
    result: List[types.InlineQueryResult] = []

    if player is None:
        # not playing
        r.add_no_game(result)
    else:
        game = player.game
        
        if not game.started:
            # game not started
            r.add_not_started(result)
        else:
            chat_settings = get_chat_settings(game.id)
            theme_name = chat_settings.card_theme if chat_settings else 'classic'
            
            playable = []  # playable cards

            if player in {game.current_player}:
                # player is ATK
                if not game.is_pass:
                    r.add_pass(result, game, theme_name)
                playable = player.playable_card_atk()
                
                sorted_cards = sorted(player.cards)
                for card_ in sorted_cards:
                    r.add_card(game, card_, result, (card_ in playable), theme_name)
                
            elif player == game.opponent_player:
                # player is DEF
                if game.field and not game.all_beaten_cards:
                    r.add_draw(player, result, theme_name)
                
                atk_card = None
                try:
                    atk_card = c.from_str(text)
                except ValueError:
                    pass

                if atk_card is None:
                    for atk in game.attacking_cards:
                        if game.field.get(atk) is None:
                            atk_card = atk
                            break
                
                if atk_card is None or atk_card not in game.attacking_cards or game.field.get(atk_card) is not None:
                    sorted_cards = sorted(player.cards)
                    for card_ in sorted_cards:
                        r.add_card(game, card_, result, False, theme_name)
                else:
                    playable = player.playable_card_def(atk_card)
                    
                    sorted_cards = sorted(player.cards)
                    for card_ in sorted_cards:
                        r.add_card(game, atk_card, result, (card_ in playable), theme_name, def_card=card_)

            else:
                # Support player
                playable = player.playable_card_atk()
                
                sorted_cards = sorted(player.cards)
                for card_ in sorted_cards:
                    r.add_card(game, card_, result, (card_ in playable), theme_name)

            r.add_gameinfo(game, result, theme_name)

        for res in result:
            res.id += ':%d' % player.anti_cheat

    await query.answer(result, cache_time=0)
