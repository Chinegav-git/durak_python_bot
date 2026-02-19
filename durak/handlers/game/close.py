from contextlib import suppress

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest

from durak.handlers.game import GameCallback
from durak.logic.game_manager import GameManager
from durak.objects.errors import NoGameInChatError

router = Router()
gm = GameManager()

@router.callback_query(GameCallback.filter(F.action == "close"))
async def close_lobby_handler(
    query: types.CallbackQuery, callback_data: GameCallback
):
    """
    Handles closing the lobby via an inline button.
    Only the game creator can perform this action.
    """
    game_id = callback_data.game_id
    user_id = query.from_user.id

    try:
        game = await gm.get_game_from_chat(game_id)
    except NoGameInChatError:
        # Game might already be closed, just update the message
        with suppress(TelegramBadRequest):
            await query.message.edit_text("Лобі вже закрито.")
        await query.answer()
        return

    # Permission Check: Only the creator can close the lobby
    if user_id != game.creator_id:
        await query.answer("Натискати може тільки творець гри!", show_alert=True)
        return

    # Correctly end the game
    await gm.end_game(game)

    # Edit the message to inform users
    with suppress(TelegramBadRequest):
        await query.message.edit_text("Лобі було закрито творцем гри.")
    
    await query.answer("Лобі закрито.")
