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

    # The message should be a reply to the winner's message
    if not message.reply_to_message:
        return await message.reply("Эта команда должна быть вызвана в ответ на сообщение игрока, которого вы хотите объявить победителем.")

    winner_id = message.reply_to_message.from_user.id
    
    try:
        await gm.test_win_game(game, winner_id)
    except ValueError as e:
        await message.reply(str(e))
