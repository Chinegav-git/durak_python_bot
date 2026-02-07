from aiogram import types
from typing import List

from loader import bot, dp, gm, CHOISE
from durak.objects import *
from durak.logic import result as r


@dp.inline_handler()
async def inline_handler(query: types.InlineQuery):
    ''' Inline handler :> '''
    user = types.User.get_current()
    text = query.query or ''
    player = gm.player_for_user(user)
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
        
            playable = []  # playable cards 

            if player in {game.current_player}:
                # player is ATK
                if not game.is_pass:
                    r.add_pass(result, game)
                playable = player.playable_card_atk()
                
                # Sort all cards and show all, but highlight only playable ones
                sorted_cards = sorted(player.cards)
                for card_ in sorted_cards:
                    r.add_card(game, card_, result, (card_ in playable), None, player)
                
            elif player == game.opponent_player:
                # player is DEF
                if game.field and not game.all_beaten_cards:
                    r.add_draw(player, result)
                
                # Try to parse attacking card from text
                atk_card = None
                try:
                    atk_card = c.from_str(text)
                except:
                    pass

                # If defender didn't specify an attacking card (e.g. didn't use the button),
                # pick the first unbeaten attacking card so the defender can still defend.
                if atk_card is None:
                    for atk in game.attacking_cards:
                        if game.field.get(atk) is None:
                            atk_card = atk
                            break
                
                if atk_card is None or atk_card not in game.attacking_cards or game.field.get(atk_card) is not None:
                    # text is empty or invalid - show all player's cards (greyed out, since no attacking card selected)
                    sorted_cards = sorted(player.cards)
                    for card_ in sorted_cards:
                        r.add_card(game, card_, result, False, None, player)
                else:
                    # atk_card is valid and unbeaten - show ALL player cards, but highlight only ones that can beat this card
                    playable = player.playable_card_def(atk_card)
                    
                    # Sort all cards and show all, but highlight only playable ones
                    sorted_cards = sorted(player.cards)
                    for card_ in sorted_cards:
                        r.add_card(game, atk_card, result, (card_ in playable), card_, player)

            else:
                # ✅ ТРЕТІЙ ГРАВЕЦЬ (support player)
                # Може підкидати карти як атакуючий (якщо вони збігаються зі значеннями на столі)
                playable = player.playable_card_atk()
                
                # Sort all cards and show all, but highlight only playable ones
                sorted_cards = sorted(player.cards)
                for card_ in sorted_cards:
                    r.add_card(game, card_, result, (card_ in playable), None, player)

            r.add_gameinfo(game, result)

        for res in result:
            res.id += ':%d' % player.anti_cheat

    await query.answer(result, cache_time=0)
    return