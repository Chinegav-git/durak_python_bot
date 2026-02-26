from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.enums import ChatType

from durak.logic import utils
from durak.logic.game_manager import GameManager
from durak.objects import NoGameInChatError

router = Router()
gm = None  # Will be initialized later

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
    can_kill = await utils.user_can_change_settings(message.bot, user.id, chat.id)
    if not (user.id == game.creator_id or can_kill):
        await message.answer(
            "🚫 Ви не можете завершити гру! "
            "Це може зробити лише творець гри або адміністратор чату."
        )
        return

    # End the game
    await gm.end_game(game)

    mention = user.first_name
    await message.answer(f"🛑 {mention} примусово завершив(ла) гру!")
