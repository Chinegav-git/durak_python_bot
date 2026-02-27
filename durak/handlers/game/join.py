# -*- coding: utf-8 -*-
"""
Модуль для обработки присоединения игроков к игре.
Отвечает за команду /join и callback-кнопку "Присоединиться".

Module for handling players joining a game.
Responsible for the /join command and the "Join" callback button.
"""

from contextlib import suppress

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ИСПРАВЛЕНО: Импорт констант команд и конфигурации.
# FIXED: Import command and configuration constants.
from config import Commands, Config
from durak.logic.game_manager import GameManager
from durak.utils.i18n import t
# ИСПРАВЛЕНО: Явный импорт исключений вместо wildcard.
# FIXED: Explicit exception imports instead of wildcard.
from durak.objects import (
    AlreadyJoinedError,
    AlreadyJoinedInGlobalError,
    GameStartedError,
    LimitPlayersInGameError,
    LobbyClosedError,
    NoGameInChatError,
)

# ИСПРАВЛЕНО: Корректный путь импорта GameCallback.
# FIXED: Correct import path for GameCallback.
from .game_callback import GameCallback

router = Router()


async def process_join(chat: types.Chat, user: types.User, gm: GameManager, game_id_from_callback: str = None):
    """
    Универсальная функция для обработки логики присоединения к игре.
    Вызывается как из обработчика команды, так и из обработчика callback\'а.

    - Проверяет наличие игры и соответствие ID.
    - Обрабатывает все возможные ошибки присоединения (игра началась, лимит игроков и т.д.).
    - В случае успеха возвращает объект игры, в случае ошибки - строку с текстом.
    
    Universal function for handling the logic of joining a game.
    Called from both the command handler and the callback handler.

    - Checks for the existence of a game and ID matching.
    - Handles all possible join errors (game started, player limit, etc.).
    - On success, returns the game object; on failure, returns a string with text.
    """
    try:
        game = await gm.get_game_from_chat(chat)
        # Сверяем ID игры из callback\'а с ID игры в чате, чтобы убедиться, что кнопка актуальна
        if game_id_from_callback and game.id != int(game_id_from_callback):
            # ИСПРАВЛЕНО: Текст переведен на русский.
            return t('game.old_button')
    except NoGameInChatError:
        # ИСПРАВЛЕНО: Текст переведен и используется константа команды.
        return f'🚫 {t("game.no_game")} {t("game.create_new")} /{Commands.NEW}'

    try:
        await gm.join_in_game(game, user)
    # ИСПРАВЛЕНО: Все сообщения об ошибках переведены на русский.
    except GameStartedError:
        return t('game.already_started')
    except LobbyClosedError:
        return t('game.game_closed')
    except LimitPlayersInGameError:
        return t('game.game_full', current=Config.MAX_PLAYERS, max=Config.MAX_PLAYERS)
    except AlreadyJoinedInGlobalError:
        # ИСПРАВЛЕНО: Текст переведен и используется константа команды.
        return f'🚫 {t("game.already_joined_elsewhere")} /{Commands.GLEAVE}'
    except AlreadyJoinedError:
        return t('game.already_joined')
    
    return game  # Возвращаем объект игры в случае успеха


@router.message(Command(Commands.JOIN), F.chat.type.in_({'group', 'supergroup'}))
async def join_command_handler(message: types.Message, gm: GameManager):
    """
    Обрабатывает команду /join.
    
    Handles the /join command.
    """
    result = await process_join(message.chat, message.from_user, gm)
    
    if isinstance(result, str):
        await message.answer(result)
    else:
        # ИСПРАВЛЕНО: Текст переведен.
        await message.answer(t('game.joined', name=message.from_user.first_name))
        # TODO: После присоединения по команде, хорошо бы обновить сообщение с лобби.
        # Это потребует хранения message_id лобби в объекте игры.


@router.callback_query(GameCallback.filter(F.action == "join"))
async def join_callback_handler(call: types.CallbackQuery, callback_data: GameCallback, gm: GameManager):
    """
    Обрабатывает нажатие на inline-кнопку "Присоединиться".
    Обновляет сообщение с лобби, добавляя нового игрока в список.

    ИСПРАВЛЕНО:
    - Добавлены полные docstring.
    - Весь текст переведен на русский.
    - Исправлен критический баг: добавлен .pack() для создания GameCallback.
    - Исправлены импорты и использование констант команд.
    - Восстановлена кнопка "Закрыть лобби" и корректное расположение кнопок.

    Handles the "Join" inline button press.
    Updates the lobby message, adding the new player to the list.

    FIXED:
    - Added full docstrings.
    - All text translated into Russian.
    - Fixed a critical bug: .pack() was added for GameCallback creation.
    - Fixed imports and usage of command constants.
    - Restored the "Close Lobby" button and the correct button layout.
    """
    result = await process_join(call.message.chat, call.from_user, gm, callback_data.game_id)
    
    if isinstance(result, str):
        await call.answer(result, show_alert=True)
        return

    game = result
    # ИСПРАВЛЕНО: Текст переведен и приведен к стандарту i18n.
    # FIXED: The text has been translated and brought to the i18n standard.
    await call.answer(t('game.join_success_alert', name=call.from_user.first_name), show_alert=False)
    
    players_list = '\n'.join([
        f'{i + 1}. {player.first_name}'
        for i, player in enumerate(game.players)
    ])
    
    # ИСПРАВЛЕНО: Добавлен .pack() и переведен текст кнопок.
    # ИСПРАВЛЕНО: Восстановлена кнопка "Закрыть лобби" и расстановка adjust(1, 2)
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t('buttons.join'), 
        callback_data=GameCallback(action="join", game_id=str(game.id)).pack()
    )
    builder.button(
        text=t('buttons.start_game'), 
        callback_data=GameCallback(action="start", game_id=str(game.id)).pack()
    )
    builder.button(
        text=t('buttons.close_lobby'),
        callback_data=GameCallback(action="close", game_id=str(game.id)).pack()
    )
    builder.adjust(1, 2)

    with suppress(TelegramBadRequest):
        # ИСПРАВЛЕНО: Текст сообщения лобби переведен на русский и использует i18n.
        # ИСПРАВЛЕНО: Отображение создателя игры теперь берется из game.creator_name.
        # FIXED: Lobby message text is translated into Russian and uses i18n.
        # FIXED: The display of the game creator is now taken from game.creator_name.
        await call.message.edit_text(
            f'{t("game.created")}\n'
            f'{t("game.creator", name=game.creator_name)}\n\n'
            f'<b>{t("game.players_list_header")}</b>\n'
            f'{players_list}\n\n'
            f'{t("game.use_buttons")}',
            reply_markup=builder.as_markup()
        )