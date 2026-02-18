
from aiogram import types
from aiogram.dispatcher.filters import Command
from loader import dp, gm, Commands
import durak.logic.actions as a
from durak.objects import NoGameInChatError
from durak.logic.actions import NotEnoughPlayersError

@dp.message_handler(Command(Commands.LEAVE), chat_type=['group', 'supergroup'])
async def leave_handler(message: types.Message):
    """ Leave a game """
    user = message.from_user
    chat = message.chat

    try:
        game = await gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await message.answer(f'🚫 У цьому чаті немає гри!\n🎮 Створіть її за допомогою - /{Commands.NEW}')
        return

    player = game.player_for_id(user.id)

    if player is None:
        await message.answer('🚫 Ви не в цій грі!')
        return

    try:
        # This action now needs to handle the DB update
        await a.do_leave_player(player)
    except NotEnoughPlayersError:
        # end_game now handles all DB updates for all players
        await gm.end_game(chat)
        await message.answer('🎮 Гра завершена, оскільки гравців не залишилося!')
    else:
        if game.started:
            await message.answer(f'👍 Добре, хід робить гравець {game.current_player.mention}')
        else:
            await message.answer(f'👋 ({user.get_mention(as_html=True)}) - Покинув(ла) лобі!')
