from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest

from durak.logic import actions
from durak.logic.game_manager import GameManager
from durak.objects import NoGameInChatError, NotEnoughPlayersError
from durak.handlers.game.game_callback import GameCallback

router = Router()
gm = None  # Will be initialized later

@router.callback_query(GameCallback.filter(F.action == "kick"))
async def lobby_kick_callback_handler(
    query: types.CallbackQuery, callback_data: GameCallback, gm: GameManager
):
    """
    Handles kicking a player from the lobby via an inline button.
    Only the game creator can perform this action.
    """
    game_id = callback_data.game_id
    creator_id = query.from_user.id
    
    try:
        user_id_to_kick = int(callback_data.value)
    except (ValueError, TypeError):
        await query.answer("Помилка: Неправильний ID гравця для кіка.", show_alert=True)
        return

    try:
        game = await gm.get_game_from_chat(game_id)
    except NoGameInChatError:
        await query.answer("Не вдалося знайти гру!", show_alert=True)
        return

    # Permission check: only the creator can kick
    if creator_id != game.creator_id:
        await query.answer("Натискати може тільки творець гри!", show_alert=True)
        return

    player_to_kick = game.player_for_id(user_id_to_kick)
    if not player_to_kick:
        await query.answer("Гравець не знайдений в цьому лобі!", show_alert=True)
        return

    kicked_player_name = player_to_kick.name

    try:
        await actions.do_leave_player(game, player_to_kick)
    except NotEnoughPlayersError:
        await gm.end_game(game)
        try:
            await query.message.edit_text("<b>Останній гравець був виключений. Лобі закрито.</b>")
        except TelegramBadRequest:
            pass # Message might have been deleted
        await query.answer("Гравець виключений, гра завершена.")
        return
    except Exception as e:
        await query.answer(f"Помилка: {e}", show_alert=True)
        return
        
    # Refresh the lobby message
    try:
        # Simple refresh without custom lobby functions
        await query.answer(f"{kicked_player_name} був(ла) виключений(а).")
    except TelegramBadRequest:
        # This can happen if the message is too old or hasn't changed.
        await query.answer("Не вдалося оновити лобі, але гравець виключений.", show_alert=True)
