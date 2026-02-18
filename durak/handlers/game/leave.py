from aiogram import types
from aiogram.dispatcher.filters import Command
from loader import dp, gm, Commands
import durak.logic.actions as a
from durak.objects.errors import NoGameInChatError, NotEnoughPlayersError

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
        await a.do_leave_player(game, player)
    except NotEnoughPlayersError:
        await gm.end_game(chat)
        await message.answer('🎮 Гра завершена, оскільки гравців не залишилося!')
    else:
        if game.started:
            await message.answer(f'👍 Добре, хід робить гравець {game.current_player.mention}')
        else:
            await message.answer(f'👋 ({user.get_mention(as_html=True)}) - Покинув(ла) лобі!')
