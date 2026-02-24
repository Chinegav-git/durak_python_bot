from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.enums import ChatType

from durak.filters.is_admin import IsAdminFilter
from durak.logic.game_manager import GameManager
from durak.objects import NoGameInChatError

router = Router()
gm = GameManager()

@router.message(
    Command("kill", "stopgame", "endgame"),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)
async def kill_game_handler(message: types.Message):
    """
    Handles commands to forcibly terminate a game.
    Can be used by the game creator or a chat admin.
    """
    user = message.from_user
    chat = message.chat

    try:
        game = await gm.get_game_from_chat(chat.id)
    except NoGameInChatError:
        await message.answer("🚫 У цьому чаті немає гри!")
        return

    # Permission check: must be creator or chat admin
    is_admin = await IsAdminFilter()(message)
    if not (user.id == game.creator_id or is_admin):
        await message.answer(
            "🚫 Ви не можете завершити гру! "
            "Це може зробити лише творець гри або адміністратор чату."
        )
        return

    # End the game
    await gm.end_game(game)

    mention = user.get_mention(as_html=True)
    await message.answer(f"🛑 {mention} примусово завершив(ла) гру!")
