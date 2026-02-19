from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.enums import ChatType

from durak.logic import actions
from durak.logic.game_manager import GameManager
from durak.objects.errors import NoGameInChatError, NotEnoughPlayersError

router = Router()
gm = GameManager()

@router.message(
    Command("leave"),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)
async def leave_game_handler(message: types.Message):
    """
    Handles a player leaving a game or lobby in the current chat.
    """
    user = message.from_user
    chat = message.chat

    try:
        game = await gm.get_game_from_chat(chat.id)
    except NoGameInChatError:
        await message.answer(
            "🚫 У цьому чаті немає гри.\n"
            "🎮 Ви можете створити її за допомогою /new"
        )
        return

    player = game.player_for_id(user.id)
    if not player:
        await message.answer("🚫 Ви не берете участь у грі в цьому чаті.")
        return

    mention = user.get_mention(as_html=True)

    try:
        await actions.do_leave_player(game, player)

        if game.started:
            # The game state (current_player) is updated within do_leave_player
            await message.answer(f"👋 {mention} покинув(ла) гру.")
        else:
            # Player left the lobby
            await message.answer(f"👋 {mention} покинув(ла) лобі.")

    except NotEnoughPlayersError:
        # This happens if the last player leaves
        await gm.end_game(game)
        await message.answer(
            f"👋 {mention} був останнім гравцем і покинув(ла) гру.\n"
            "🎮 Гра завершена!"
        )
    except Exception as e:
        await message.reply(f"Під час виходу з гри сталася помилка: {e}")
