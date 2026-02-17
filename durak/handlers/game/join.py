from aiogram import types
from loader import dp, gm, Config, Commands
from durak.objects import (
    NoGameInChatError,
    GameStartedError,
    LobbyClosedError,
    LimitPlayersInGameError,
    AlreadyJoinedInGlobalError,
    AlreadyJoinedError,
)

@dp.message_handler(commands=[Commands.JOIN], chat_type=['group', 'supergroup'])
async def join_handler(message: types.Message):
    """ Join in a game """
    user = message.from_user
    chat = message.chat

    try:
        game = await gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await message.answer(f'🚫 У цьому чаті немає гри!\n🎮 Створіть її за допомогою - /{Commands.NEW}')
        return
    
    try:
        # add user in a game
        await gm.join_in_game(game, user)
    except GameStartedError:
        await message.answer('🎮 Гра вже запущена! 🚫 Ви не можете приєднатися!')
    except LobbyClosedError:
        await message.answer('🚫 Лобі закрито!')
    except LimitPlayersInGameError:
        await message.answer(f'🚫 Досягнуто ліміт у {Config.MAX_PLAYERS} гравців!')
    except AlreadyJoinedInGlobalError:
        await message.answer(f'🚫 Схоже ви граєте в іншому чаті!\n👋 Покинути цю гру - /{Commands.GLEAVE}')
    except AlreadyJoinedError:
        await message.answer('🎮 Ви вже в грі!')
        
    else:
        await message.answer(f'👋 {user.get_mention(as_html=True)} приєднався до гри!')
