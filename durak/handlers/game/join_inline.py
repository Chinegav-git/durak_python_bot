from aiogram import types
from aiogram.utils.exceptions import MessageNotModified
from contextlib import suppress
from loader import bot, dp, gm, Config, Commands
from durak.objects import *

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('join_game'))
async def join_inline_handler(callback_query: types.CallbackQuery):
    user = callback_query.from_user
    chat = callback_query.message.chat

    try:
        game = gm.get_game_from_chat(chat)
    except NoGameInChatError:
        await bot.answer_callback_query(callback_query.id, f'🚫 У цьому чаті немає гри! Створіть її за допомогою - /{Commands.NEW}')
        return

    try:
        gm.join_in_game(game, user)
    except GameStartedError:
        await bot.answer_callback_query(callback_query.id, '🎮 Гра вже запущена! 🚫 Ви не можете приєднатися!')
    except LobbyClosedError:
        await bot.answer_callback_query(callback_query.id, '🚫 Лобі закрито!')
    except LimitPlayersInGameError:
        await bot.answer_callback_query(callback_query.id, f'🚫 Досягнуто ліміт у {Config.MAX_PLAYERS} гравців!')
    except AlreadyJoinedInGlobalError:
        await bot.answer_callback_query(callback_query.id, f'🚫 Схоже ви граєте в іншому чаті! Покинути цю гру - /{Commands.GLEAVE}')
    except AlreadyJoinedError:
        await bot.answer_callback_query(callback_query.id, '🎮 Ви вже в грі!')
    else:
        await bot.answer_callback_query(callback_query.id, f'👋 {user.first_name} приєднався до гри!')
        
        players_list = '\n'.join([
            f'{i+1}. {player.user.get_mention(as_html=True)}'
            for i, player in enumerate(game.players)
        ])
        
        join_button = types.InlineKeyboardButton(text='👋 Приєднатися', callback_data=f'join_game_{game.creator.id}')
        start_button = types.InlineKeyboardButton(text='🚀 Почати гру', callback_data=f'start_game_{game.creator.id}')
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[join_button], [start_button]])

        with suppress(MessageNotModified):
            await bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                text=f'🎮 Гру створено!\n'
                     f'👤 Засновник: {game.creator.get_mention(as_html=True)}\n\n'
                     f'<b>Гравці:</b>\n{players_list}\n\n'
                     f'Використовуйте кнопки нижче для керування грою:',
                reply_markup=keyboard
            )
