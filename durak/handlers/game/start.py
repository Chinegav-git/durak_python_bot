# -*- coding: utf-8 -*-
"""
Модуль для обработки начала игры.
Отвечает за команду /start и callback-кнопку "Начать игру",
а также отправляет сообщение о старте раунда.

Module for handling the start of a game.
Responsible for the /start command and the "Start Game" callback button,
and sends the round start message.
"""

from contextlib import suppress

from aiogram import Bot, F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ИСПРАВЛЕНО: Импорт констант и нужных моделей/классов
# FIXED: Import constants and necessary models/classes
# ИСПРАВЛЕНО (стабилизация): Удален импорт pony.orm, используется ChatSetting из .db.models
# FIXED (stabilization): Removed pony.orm import, using ChatSetting from .db.models
from config import Commands
from durak.db.models import ChatSetting
from durak.logic.game_manager import GameManager
from durak.logic.utils import user_is_creator_or_admin
from durak.objects import (
    Game, 
    GameStartedError, 
    NoGameInChatError, 
    NotEnoughPlayersError
)
from durak.objects.theme import get_sticker_id
from durak.utils.i18n import t

# ИСПРАВЛЕНО: Корректный импорт GameCallback
# FIXED: Correct import of GameCallback
from .game_callback import GameCallback

router = Router()


async def send_game_start_message(bot: Bot, chat_id: int, game: Game):
    """
    Отправляет сообщение о начале игры: козырь, кто ходит, и игровую клавиатуру.
    
    ИСПРАВЛЕНО:
    - Логика получения настроек чата заменена на PonyORM.
    - Весь текст переведен на русский.
    - Создана временная, но технически корректная клавиатура.
    
    ИСПРАВЛЕНО (стабилизация): 
    - Запрос к БД заменен с PonyORM на асинхронный Tortoise-ORM.

    Sends the game start message: trump, current player, and the game keyboard.

    FIXED:
    - Chat settings retrieval logic replaced with PonyORM.
    - All text translated into Russian.
    - A temporary but technically correct keyboard has been created.

    FIXED (stabilization):
    - DB query replaced from PonyORM to asynchronous Tortoise-ORM.
    """
    settings = await ChatSetting.get_or_none(chat_id=chat_id)
    theme_name = settings.card_theme if settings else 'classic'
    
    trump_sticker_id = get_sticker_id(game.trump.value, theme_name)
    if trump_sticker_id:
        with suppress(TelegramBadRequest):
            await bot.send_sticker(chat_id, trump_sticker_id)

    current = game.current_player
    opponent = game.opponent_player
    
    # ИСПРАВЛЕНО: Все строки переведены и используют i18n.
    # FIXED: All strings are translated and use i18n.
    text = (
        f"🎯 <b>{t('round.start_header')}</b>\n\n"
        f"⚔️ {t('round.attacker', name=current.mention, count=len(current.cards))}\n"
        f"🛡️ {t('round.defender', name=opponent.mention, count=len(opponent.cards))}\n\n"
        f"🃏 {t('round.trump', trump_icon=game.deck.trump_ico)}\n"
        f"🃏 {t('round.deck_cards_count', count=len(game.deck.cards))}"
    )
    
    # ИСПРАВЛЕНО: Клавиатура-заглушка заменена на рабочую временную клавиатуру
    builder = InlineKeyboardBuilder()
    builder.button(text=t('buttons.my_cards'), switch_inline_query_current_chat='')
    builder.adjust(1)
    
    await bot.send_message(chat_id, text, reply_markup=builder.as_markup())


async def process_start(bot: Bot, chat: types.Chat, user: types.User, gm: GameManager, game_id_from_callback: str = None):
    """
    Универсальная функция для обработки логики начала игры.

    ИСПРАВЛЕНО:
    - Тип game_id_from_callback изменен на str.
    - Все сообщения переведены на русский.
    - Используются константы команд.
    
    ИСПРАВЛЕНО (стабилизация):
    - Добавлен аргумент `bot` для передачи в `user_is_creator_or_admin`.
    - Исправлен вызов `user_is_creator_or_admin` с корректными аргументами.

    Generic function to handle the logic of starting a game.

    FIXED:
    - The type of game_id_from_callback changed to str.
    - All messages translated into Russian.
    - Using command constants.

    FIXED (stabilization):
    - Added `bot` argument to be passed to `user_is_creator_or_admin`.
    - Fixed the call to `user_is_creator_or_admin` with correct arguments.
    """
    try:
        game = await gm.get_game_from_chat(chat)
        if game_id_from_callback and game.id != int(game_id_from_callback):
            return t('game.old_button')
    except NoGameInChatError:
        return f'🚫 {t("game.no_game")} {t("game.create_new")} /{Commands.NEW}'
    
    if not (await user_is_creator_or_admin(bot, user.id, game, chat.id)):
        return t('game.start_permission_denied')

    try:
        await gm.start_game(game)
    except GameStartedError:
        return t('game.already_started')
    except NotEnoughPlayersError:
        return f'🚫 {t("game.not_enough_players")} {t("game.join_suggestion")} /{Commands.JOIN}'
    
    return game


@router.message(Command(Commands.START), F.chat.type.in_(({'group', 'supergroup'})))
async def start_command_handler(message: types.Message, bot: Bot, gm: GameManager):
    """
    Обрабатывает команду /start для начала игры.
    Handles the /start command to begin a game.
    """
    result = await process_start(bot, message.chat, message.from_user, gm)
    
    if isinstance(result, str):
        await message.answer(result)
    else:
        game = result
        await message.answer(t('game.started_successfully'))
        await send_game_start_message(bot, message.chat.id, game)


@router.callback_query(GameCallback.filter(F.action == "start"))
async def start_callback_handler(call: types.CallbackQuery, callback_data: GameCallback, bot: Bot, gm: GameManager):
    """
    Обрабатывает нажатие на inline-кнопку "Начать игру".
    Handles the "Start Game" inline button press.
    """
    result = await process_start(bot, call.message.chat, call.from_user, gm, callback_data.game_id)
    
    if isinstance(result, str):
        await call.answer(result, show_alert=True)
        return

    game = result
    await call.answer(t('game.started_successfully'), show_alert=False)
    
    # Удаляем сообщение с лобби, так как игра началась
    with suppress(TelegramBadRequest):
        await call.message.delete()

    await send_game_start_message(bot, call.message.chat.id, game)
