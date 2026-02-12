from aiogram import types
from loader import dp, gm
from durak.objects.errors import NoGameInChatError


@dp.message_handler(commands=["test_win"], is_admin=True)
async def test_win(message: types.Message):
    """
    Handler for /test_win command to instantly end the game with a winner.
    Available only for admins.
    """
    try:
        game = gm.get_game_from_chat(message.chat)
    except NoGameInChatError:
        return await message.reply("Игра в этом чате не найдена.")

    args = message.get_args()
    winner_id = None

    if message.reply_to_message:
        winner_id = message.reply_to_message.from_user.id
    elif args:
        try:
            winner_id = int(args)
        except ValueError:
            return await message.reply("Неверный ID пользователя. ID должен быть числом.")
    else:
        return await message.reply(
            "Эта команда должна быть вызвана в ответ на сообщение игрока или с указанием ID игрока, "
            "которого вы хотите объявить победителем."
        )

    if not game.player_for_id(winner_id):
        return await message.reply("Игрок с таким ID не найден в этой игре.")
        
    try:
        await gm.test_win_game(game, winner_id)
    except ValueError as e:
        await message.reply(str(e))
