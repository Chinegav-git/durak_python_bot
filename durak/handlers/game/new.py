# -*- coding: utf-8 -*-
"""
Модуль для обработки создания новой игры.
Отвечает за команду /new и инициализацию игрового лобби.

Module for handling the creation of a new game.
Responsible for the /new command and initializing the game lobby.
"""

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from durak.logic.game_manager import GameManager
from durak.objects import GameAlreadyInChatError, AlreadyJoinedInGlobalError

# ИСПРАВЛЕНО: Импортируем GameCallback из правильного модуля.
# FIXED: Importing GameCallback from the correct module.
from .game_callback import GameCallback

# ИСПРАВЛЕНО: Импортируем константы команд.
# FIXED: Importing command constants.
from config import Commands

router = Router()


@router.message(Command(Commands.NEW), F.chat.type.in_({'group', 'supergroup'}))
async def new_game_handler(message: types.Message, gm: GameManager):
    """
    Обрабатывает команду /new для создания новой игры в групповом чате.

    - Проверяет, нет ли уже активной игры в этом чате.
    - Проверяет, не участвует ли создатель уже в другой игре.
    - Создает игру и отправляет сообщение с лобби и кнопками для входа/старта.
    
    ИСПРАВЛЕНО:
    - Добавлены полные русские и английские docstring.
    - Весь текст, обращенный к пользователю, переведен на русский.
    - Исправлена критическая ошибка: добавлен .pack() при создании GameCallback.
    - Используется константа команды Commands.NEW.
    - Скорректировано расположение кнопок в клавиатуре для лучшего UX.
    ДОБАВЛЕНО:
    - В клавиатуру лобби добавлена кнопка "Закрыть лобби".

    Handles the /new command to create a new game in a group chat.

    - Checks if there is already an active game in this chat.
    - Checks if the creator is already participating in another game.
    - Creates the game and sends a message with the lobby and buttons to join/start.

    FIXED:
    - Added full Russian and English docstrings.
    - All user-facing text has been translated into Russian.
    - Fixed a critical error: .pack() was added when creating GameCallback.
    - Using the Commands.NEW command constant.
    - Adjusted button layout in the keyboard for better UX.
    ADDED:
    - Added a "Close Lobby" button to the lobby keyboard.
    """
    user = message.from_user
    chat = message.chat

    try:
        game = await gm.new_game(chat, creator=user)
    except GameAlreadyInChatError:
        # ИСПРАВЛЕНО: Текст переведен на русский.
        await message.answer('🚫 В этом чате уже есть игра.')
        return
    except AlreadyJoinedInGlobalError:
        # ИСПРАВЛЕНО: Текст переведен на русский.
        await message.answer('🚫 Вы уже находитесь в другой игре.')
        return

    # ИСПРАВЛЕНО: Создание клавиатуры с использованием .pack()
    builder = InlineKeyboardBuilder()
    builder.button(
        text='👋 Присоединиться',
        callback_data=GameCallback(action="join", game_id=str(game.id)).pack()
    )
    builder.button(
        text='🚀 Начать игру',
        callback_data=GameCallback(action="start", game_id=str(game.id)).pack()
    )
    builder.button(
        text='🔒 Закрыть лобби',
        callback_data=GameCallback(action="close", game_id=str(game.id)).pack()
    )
    builder.adjust(1, 2)
    
    # ИСПРАВЛЕНО: Текст переведен на русский.
    await message.answer(
        f'🎮 Игра создана!\n'
        f'👤 Создатель: {user.get_mention(as_html=True)}\n\n'
        f'Используйте кнопки ниже для управления игрой:',
        reply_markup=builder.as_markup()
    )
