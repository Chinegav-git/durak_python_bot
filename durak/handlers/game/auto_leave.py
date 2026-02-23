# -*- coding: utf-8 -*-
"""
Модуль для автоматического исключения игрока из игры, 
когда он покидает чат или его исключают.

Module for automatically removing a player from a game
when they leave or are kicked from the chat.
"""

from aiogram import F, Router, types
from aiogram.enums import ChatType

from durak.logic import actions
from durak.logic.game_manager import GameManager
from durak.objects.errors import NoGameInChatError, NotEnoughPlayersError

router = Router()
gm = GameManager()


@router.message(
    F.left_chat_member,
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)
async def auto_leave_on_chat_leave_handler(message: types.Message):
    """
    Автоматически исключает игрока из игры, если он покинул групповой чат.

    - Срабатывает на системное сообщение о выходе пользователя.
    - Проверяет, был ли вышедший пользователь участником игры в этом чате.
    - Если да, исключает его и уведомляет чат.
    - Если после выхода игрока остается недостаточно для продолжения,
      завершает игру.

    ИСПРАВЛЕНО:
    - Добавлены полные docstring.
    - Весь текст переведен на русский язык.
    - Исправлен аргумент в `get_game_from_chat` (передан объект `chat`).
    
    Automatically removes a player from a game if they leave the group chat.

    - Triggers on the system message about a user leaving.
    - Checks if the user who left was a participant in the game in this chat.
    - If so, removes them and notifies the chat.
    - If not enough players remain after they leave, the game is ended.

    FIXED:
    - Added full docstrings.
    - All text translated into Russian.
    - Fixed the argument in `get_game_from_chat` (passing the `chat` object).
    """
    user_left = message.left_chat_member
    if not user_left:
        return

    chat = message.chat

    try:
        # ИСПРАВЛЕНО: передаем объект `chat`, а не `chat.id`.
        # FIXED: passing the `chat` object, not `chat.id`.
        game = await gm.get_game_from_chat(chat)
    except NoGameInChatError:
        return  # В этом чате нет игры, ничего не делаем.

    player_to_remove = game.player_for_id(user_left.id)
    if not player_to_remove:
        return  # Пользователь, покинувший чат, не был игроком.

    mention = user_left.get_mention(as_html=True)

    try:
        await actions.do_leave_player(game, player_to_remove)
        
        # ИСПРАВЛЕНО: Текст переведен на русский.
        await message.answer(
            f"👋 {mention} покинул(а) чат и был(а) автоматически "
            "исключен(а) из игры."
        )

    except NotEnoughPlayersError:
        # TODO: Эту логику можно инкапсулировать в do_leave_player
        # или в game_manager.end_game для чистоты кода.
        await gm.end_game(game)
        # ИСПРАВЛЕНО: Текст переведен на русский.
        await message.answer(
            f"👋 {mention} покинул(а) чат. В игре осталось недостаточно "
            "участников.\n🎮 Игра завершена!"
        )
    except Exception as e:
        # В реальном приложении здесь должно быть логирование ошибки.
        # In a real application, there should be error logging here.
        await message.answer(
            f"Произошла ошибка при автоматическом исключении игрока: {e}"
        )
