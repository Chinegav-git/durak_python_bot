from aiogram import types
from aiogram.dispatcher.filters import Command
from loader import bot, dp, gm, Commands
import durak.logic.actions as a
from durak.objects.errors import NoGameInChatError, NotEnoughPlayersError

@dp.message_handler(Command(Commands.GLEAVE))
async def global_leave_handler(message: types.Message):
    """ Global leave from any game """
    user = message.from_user
    
    game_id = await gm.get_user_game_id(user.id)
    if not game_id:
        await message.answer('🚫 Ви не граєте в жодній грі!')
        return

    try:
        game = await gm.get_game_from_chat(game_id)
    except NoGameInChatError:
        # This case should ideally not happen if the user_game key is consistent
        await gm.redis.delete(gm._user_game_key(user.id)) # Clean up inconsistent state
        await message.answer('🚫 Помилка: гри, в якій ви брали участь, не знайдено. Ваш статус оновлено.')
        return

    player = game.player_for_id(user.id)
    if not player:
        # This case should also ideally not happen
        await gm.redis.delete(gm._user_game_key(user.id)) # Clean up inconsistent state
        await message.answer('🚫 Помилка: вас не знайдено в грі, в якій ви нібито берете участь. Ваш статус оновлено.')
        return
    
    mention = user.get_mention(as_html=True)

    try:
        await a.do_leave_player(game, player)
        await message.answer(f'👋 Ви успішно покинули гру в чаті "{game.chat_title_or_id()}"!')

    except NotEnoughPlayersError:
        await gm.end_game(game)
        await bot.send_message(game.id, f'👋 {mention} покинув(ла) гру!\n🎮 Гра завершена, оскільки не залишилося гравців.')
        await message.answer(f'👋 Ви успішно покинули гру, і її було завершено, оскільки ви були останнім гравцем.')
    
    except Exception as e:
        await message.answer(f"Сталася несподівана помилка: {e}")

    else:
        # Notify other players in the game chat
        if game.id != message.chat.id: # Avoid double notification
            if game.started:
                await bot.send_message(game.id, f'👋 {mention} покинув(ла) гру.\n🎯 Хід робить гравець {game.current_player.mention}')
            else:
                await bot.send_message(game.id, f'👋 {mention} покинув(ла) лоббі!')
