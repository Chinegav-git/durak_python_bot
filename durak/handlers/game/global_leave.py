from aiogram import Router, Bot, types
from aiogram.filters import Command

from durak.logic import actions
from durak.logic.game_manager import GameManager
from durak.objects import NoGameInChatError, NotEnoughPlayersError

router = Router()


@router.message(Command("global_leave", "gleave", "leave_all"))
async def global_leave_handler(message: types.Message, bot: Bot, gm: GameManager):
    """
    Handles a user leaving any game they are currently participating in.
    This command can be sent in any chat (e.g., private messages with the bot).
    """
    user = message.from_user

    game_id = await gm.get_user_game_id(user.id)
    if not game_id:
        await message.answer("🚫 Ви не берете участь у жодній грі!")
        return

    try:
        game = await gm.get_game_from_chat(game_id)
    except NoGameInChatError:
        # Clean up inconsistent state where a user is linked to a non-existent game
        await gm.redis.delete(gm._user_game_key(user.id))
        await message.answer(
            "🚫 Помилка: гри, в якій ви нібито брали участь, більше не існує. "
            "Ваш ігровий статус було скинуто."
        )
        return

    player = game.player_for_id(user.id)
    if not player:
        # Clean up inconsistent state where a user is linked to a game they are not in
        await gm.redis.delete(gm._user_game_key(user.id))
        await message.answer(
            "🚫 Помилка: вас не знайдено в грі, до якої ви були прив'язані. "
            "Ваш ігровий статус було скинуто."
        )
        return

    mention = user.first_name
    game_chat_id = game.id
    chat_title = game.chat_title

    try:
        await actions.do_leave_player(game, player, gm, message.bot)

        # Notify the user who sent the command
        await message.answer(f'👋 Ви успішно покинули гру в чаті "{chat_title}".')

        # Notify the game chat, if it's a different chat
        if game_chat_id != message.chat.id:
            await bot.send_message(game_chat_id, f"👋 {mention} покинув(ла) гру.")

    except NotEnoughPlayersError:
        await gm.end_game(game)
        
        # Notify the user who sent the command
        await message.answer(
            f'👋 Ви покинули гру в чаті "{chat_title}", і вона була завершена, '
            '"оскільки ви були останнім гравцем."'
        )
        
        # Notify the game chat, if it's a different chat
        if game_chat_id != message.chat.id:
            await bot.send_message(
                game_chat_id,
                f"👋 {mention} покинув(ла) гру як останній гравець.\n"
                '"🎮 Гра завершена!"',
            )

    except Exception as e:
        await message.answer(f"Сталася несподівана помилка при виході з гри: {e}")
