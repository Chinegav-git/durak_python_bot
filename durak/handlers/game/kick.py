from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.enums import ChatType

from durak.logic import actions, utils
from durak.logic.game_manager import GameManager
from durak.objects import NoGameInChatError, NotEnoughPlayersError

router = Router()


@router.message(
    Command("kick"),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
    F.reply_to_message
)
async def kick_in_game_handler(message: types.Message, gm: GameManager):
    """
    Handles the /kick command during an active game.
    Requires a reply to the message of the user to be kicked.
    Can be used by the game creator or a chat admin.
    """
    kicker_user = message.from_user
    kicked_user = message.reply_to_message.from_user
    chat = message.chat

    if kicked_user.is_bot:
        await message.reply("Ви не можете виключити бота.")
        return

    try:
        game = await gm.get_game_from_chat(chat.id)
    except NoGameInChatError:
        await message.answer("🚫 У цьому чаті немає гри!")
        return

    kicked_player = game.player_for_id(kicked_user.id)
    if not kicked_player:
        await message.reply("🚫 Цей користувач не бере участі в грі.")
        return
        
    if not await utils.user_can_kick(message.bot, kicker_user.id, chat, game):
        await message.reply(
            "🚫 Ви не можете виключати гравців. "
            "Це може зробити тільки творець гри або адміністратор чату."
        )
        return

    if kicked_player.id == game.creator_id:
        await message.reply("🚫 Неможливо виключити творця гри.")
        return

    kicked_mention = kicked_user.first_name
    kicker_mention = kicker_user.first_name

    try:
        # ИСПРАВЛЕНО (рефакторинг): Передаем gm и bot в функцию
        await actions.do_leave_player(game, kicked_player, gm, message.bot)
        
        if game.started:
            await message.answer(
                f"👋 {kicked_mention} був(ла) виключений(а) гравцем {kicker_mention}."
            )
        else:
            await message.answer(
                f"👋 {kicked_mention} був(ла) виключений(а) гравцем {kicker_mention} з лоббі!"
            )

    except NotEnoughPlayersError:
        await gm.end_game(game)
        await message.answer(
            f"👋 {kicked_mention} був(ла) виключений(а) гравцем {kicker_mention}.\n"
            "🎮 Гра завершена, оскільки гравців більше немає!"
        )
    except Exception as e:
        await message.reply(f"Сталася помилка при виключенні гравця: {e}")
