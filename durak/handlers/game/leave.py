from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.enums import ChatType

from durak.logic import actions
from durak.logic.game_manager import GameManager
from durak.objects import NoGameInChatError, NotEnoughPlayersError
from durak.utils.i18n import t

router = Router()


@router.message(
    Command("leave"),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)
async def leave_game_handler(message: types.Message, gm: GameManager):
    """
    Handles a player leaving a game or lobby in the current chat.
    """
    user = message.from_user
    chat = message.chat

    try:
        game = await gm.get_game_from_chat(chat.id)
    except NoGameInChatError:
        await message.answer(
            f"{t('game.no_game')}\n"
            f"{t('game.create_new')}"
        )
        return

    player = game.player_for_id(user.id)
    if not player:
        await message.answer(t('game.not_participating'))
        return

    mention = user.first_name

    try:
        # ИСПРАВЛЕНО (рефакторинг): Передаем gm и bot в функцию
        await actions.do_leave_player(game, player, gm, message.bot)

        if game.started:
            # The game state (current_player) is updated within do_leave_player
            await message.answer(t('game.left_game', name=mention))
        else:
            # Player left the lobby
            await message.answer(t('game.left_lobby', name=mention))

    except NotEnoughPlayersError:
        # This happens if the last player leaves
        await gm.end_game(game)
        await message.answer(
            f"{t('game.last_player_left', name=mention)}\n"
            "🎮 Гра завершена!"
        )
    except Exception as e:
        await message.reply(t('errors.unexpected', error=e))
