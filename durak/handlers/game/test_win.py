from aiogram import types
from loader import dp, gm, Commands
from durak.objects.errors import NoGameInChatError


@dp.message_handler(commands=[Commands.TEST_WIN], is_admin=True)
async def test_win(message: types.Message):
    """
    Handler for /test_win command to instantly end the game with a winner.
    Available only for admins.
    """
    try:
        game = await gm.get_game_from_chat(message.chat)
    except NoGameInChatError:
        return await message.reply("Гру в цьому чаті не знайдено.")

    args = message.get_args()
    winner_id = None

    if message.reply_to_message:
        winner_id = message.reply_to_message.from_user.id
    elif args:
        try:
            winner_id = int(args)
        except ValueError:
            return await message.reply("Неправильний ID користувача. ID має бути числом.")
    else:
        return await message.reply(
            "Ця команда має бути викликана у відповідь на повідомлення гравця або з зазначенням ID гравця, "
            "якого ви хочете оголосити переможцем."
        )

    if not game.player_for_id(winner_id):
        return await message.reply("Гравця з таким ID не знайдено в цій грі.")
        
    try:
        await gm.test_win_game(game, winner_id)
    except ValueError as e:
        await message.reply(str(e))
