from aiogram import F, Router, types
from aiogram.enums import ChatType

from durak.logic import actions
from durak.logic.game_manager import GameManager
from durak.objects.errors import NoGameInChatError, NotEnoughPlayersError

router = Router()
gm = GameManager()

@router.message(
    F.left_chat_member,
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)
async def auto_leave_on_chat_leave_handler(message: types.Message):
    """
    Automatically removes a player from a game if they leave the group chat.
    """
    user_left = message.left_chat_member
    if not user_left:
        return  # Should not happen with this filter, but as a safeguard

    chat = message.chat

    try:
        game = await gm.get_game_from_chat(chat.id)
    except NoGameInChatError:
        return  # No game in this chat, nothing to do.

    player_to_remove = game.player_for_id(user_left.id)
    if not player_to_remove:
        return  # The user who left was not a player.

    mention = user_left.get_mention(as_html=True)

    try:
        await actions.do_leave_player(game, player_to_remove)
        
        # Notify the chat that the player was removed.
        await message.answer(
            f"👋 {mention} покинув(ла) чат, тому був(ла) автоматично "
            "виключений(а) з гри."
        )

    except NotEnoughPlayersError:
        await gm.end_game(game)
        await message.answer(
            f"👋 {mention} покинув(ла) чат як останній гравець.\n"
            "🎮 Гра завершена!"
        )
    except Exception as e:
        # Log this error properly in a real application
        await message.answer(
            f"Сталася помилка при автоматичному виключенні гравця: {e}"
        )
