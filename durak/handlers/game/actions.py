from aiogram import F, Router, types

from durak.logic import actions
from durak.logic.game_manager import GameManager
from durak.objects.card import Card
from durak.objects.errors import NoGameInChatError
from durak.handlers.game import GameCallback

router = Router()
gm = GameManager()


@router.message(F.text.regexp(r"^(Карта|Стікер): ([♦️♣️♥️♠️].*)$"))
async def process_card_move_handler(message: types.Message):
    """
    Handles a message that represents a card move (attack or defense).
    This is triggered when a user selects a card from the inline menu.
    """
    user = message.from_user
    card_str = message.text.split(": ", 1)[1]

    try:
        game = await gm.get_game_by_user_id(user.id)
        if not game or not game.started:
            return
        
        player = game.player_for_id(user.id)
        if not player:
            return

        # Determine if it's an attack or defense based on the player's role
        # This is a simplified approach. The actual card validation is inside the action.
        
        # Defense move
        if player == game.opponent_player and game.table:
            # We need the attacking card to defend against.
            # The inline query should have provided this context.
            # Since we can't get it directly here, we assume the player chose a valid defense.
            # This relies on the client-side logic being correct.
            # A more robust solution would involve passing context via the message.
            # For now, we find the first undefended card.
            
            undefended_card = game.table.get_first_undefended()
            if not undefended_card:
                return # Should not happen in a defense scenario
            
            def_card = Card.from_str(card_str)
            if not def_card:
                return

            await actions.do_defence_card(game, player, undefended_card, def_card)

        # Attack/Throw-in move
        elif player in (game.current_player, game.support_player):
            atk_card = Card.from_str(card_str)
            if not atk_card:
                return
            
            await actions.do_attack_card(game, player, atk_card)

    except NoGameInChatError:
        pass # Ignore if the user is not in a game
    finally:
        # Clean up the message that triggered the move
        await message.delete()


@router.callback_query(GameCallback.filter(F.action == "take"))
async def take_cards_callback_handler(call: types.CallbackQuery, callback_data: GameCallback):
    """ Handles the 'Take' button press. """
    try:
        game = await gm.get_game_from_chat(callback_data.game_id)
        player = game.player_for_id(call.from_user.id)

        if player and player == game.opponent_player:
            await actions.do_draw(game, player)
    
    except NoGameInChatError:
        pass
    finally:
        await call.answer()


@router.callback_query(GameCallback.filter(F.action == "pass"))
async def pass_turn_callback_handler(call: types.CallbackQuery, callback_data: GameCallback):
    """ Handles the 'Pass' (Bito) button press. """
    try:
        game = await gm.get_game_from_chat(callback_data.game_id)
        player = game.player_for_id(call.from_user.id)

        if player and player in (game.current_player, game.support_player):
            await actions.do_pass(game, player)
            
    except NoGameInChatError:
        pass
    finally:
        await call.answer()
