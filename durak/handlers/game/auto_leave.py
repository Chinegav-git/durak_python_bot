from aiogram import types
from loader import bot, dp, gm
import durak.logic.actions as a
from durak.objects import *

@dp.message_handler(content_types=[types.ContentTypes.LEFT_CHAT_MEMBER], chat_type=['group', 'supergroup'])
async def auto_leave_handler(message: types.Message):
    """ Automatically remove players who leave the group chat """
    user_left = message.left_chat_member
    if not user_left:
        return

    chat = message.chat

    try:
        game = await gm.get_game_from_chat(chat)
    except NoGameInChatError:
        return

    player_left = game.player_for_user(user_left)

    if not player_left:
        return

    mention = user_left.get_mention(as_html=True)

    try:
        # The action handles DB updates and game state
        await a.do_leave_player(player_left)
    except NotEnoughPlayersError:
        await gm.end_game(chat)
        await bot.send_message(chat.id, f'👋 ({mention}) покинув(ла) чат, і гра була завершена, оскільки не залишилося гравців.')
    else:
        if game.started:
            await bot.send_message(chat.id, f'👋 ({mention}) покинув(ла) чат, тому був(ла) виключений(а) з гри.\n🎯 Хід робить гравець {game.current_player.mention}')
        else:
            await bot.send_message(chat.id, f'👋 ({mention}) покинув(ла) чат і був(ла) виключений(а) з лоббі.')
