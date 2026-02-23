# -*- coding: utf-8 -*-
"""
Модуль для генерации результатов инлайн-режима.

Этот модуль отвечает за преобразование текущего состояния игры (Game, Player)
в список объектов `InlineQueryResult`, которые Telegram отображает пользователю
в виде подсказок над полем ввода. Каждый результат представляет собой возможное
действие (например, походить картой, взять, пас) или информационное сообщение.

------------------------------------------------------------------------------

Module for generating inline mode results.

This module is responsible for converting the current game state (Game, Player)
into a list of `InlineQueryResult` objects, which Telegram displays to the user
as suggestions above the input field. Each result represents a possible
action (e.g., play a card, draw, pass) or an informational message.
"""

from typing import List
from uuid import uuid4

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResult,
    InlineQueryResultArticle,
    InlineQueryResultCachedSticker as Sticker,
    InputTextMessageContent,
)

from config import Commands
from ..objects import Card, Game, Player, theme as th


def add_no_game(results: List[InlineQueryResult]):
    """
    Добавляет сообщение о том, что пользователь не участвует в игре.

    Args:
        results: Список, в который добавляется результат.

    Adds a message indicating that the user is not participating in a game.

    Args:
        results: The list to which the result is added.
    """
    results.append(
        InlineQueryResultArticle(
            id="nogame",
            title="🎮 Вы не играете",
            input_message_content=InputTextMessageContent(
                '🚫 Вы сейчас не играете. Используйте /new чтобы '
                'начать игру или /join, чтобы присоединиться к '
                'текущей игре в этой группе'
            ),
        )
    )


def add_not_started(results: List[InlineQueryResult]):
    """
    Добавляет сообщение о том, что игра еще не началась.

    Args:
        results: Список, в который добавляется результат.

    Adds a message indicating that the game has not yet started.

    Args:
        results: The list to which the result is added.
    """
    results.append(
        InlineQueryResultArticle(
            id="notstarted",
            title="⏳ Игра еще не началась",
            input_message_content=InputTextMessageContent(
                f'🚀 Начать игру: /{Commands.START}'
            ),
        )
    )


def add_draw(game: Game, player: Player, results: List[InlineQueryResult], theme_name: str):
    """
    Добавляет опцию "Взять карты" в виде стикера.

    Args:
        game: Текущий объект игры.
        player: Игрок, для которого генерируется результат.
        results: Список, в который добавляется результат.
        theme_name: Название темы карт для выбора правильного стикера.

    Adds a "Draw cards" option as a sticker.

    Args:
        game: The current game object.
        player: The player for whom the result is being generated.
        results: The list to which the result is added.
        theme_name: The name of the card theme to select the correct sticker.
    """
    sticker_id = th.get_sticker_id('draw', theme_name)
    if not sticker_id:
        return

    results.append(
        Sticker(
            id="draw",
            sticker_file_id=sticker_id,
            input_message_content=InputTextMessageContent(
                f"🎴 {player.mention} взял(а) карты!"
            ),
        )
    )


def add_pass(game: Game, results: List[InlineQueryResult], theme_name: str):
    """
    Добавляет опцию "Пас" в виде стикера.

    Args:
        game: Текущий объект игры.
        results: Список, в который добавляется результат.
        theme_name: Название темы карт для выбора правильного стикера.

    Adds a "Pass" option as a sticker.

    Args:
        game: The current game object.
        results: The list to which the result is added.
        theme_name: The name of the card theme to select the correct sticker.
    """
    sticker_id = th.get_sticker_id('pass', theme_name)
    if not sticker_id:
        return

    results.append(
        Sticker(
            id="pass",
            sticker_file_id=sticker_id,
            input_message_content=InputTextMessageContent('✅ Пас'),
        )
    )


def add_card(
    game: Game,
    atk_card: Card,
    results: List[InlineQueryResult],
    can_play: bool,
    theme_name: str,
    def_card: Card = None,
):
    """
    Добавляет опцию, представляющую собой игральную карту.
    
    Стиль стикера (серый или цветной) зависит от того, может ли игрок
    походить/побить этой картой. ID результата формируется из строкового
    представления карты (или карт, в случае защиты).

    Args:
        game: Текущий объект игры.
        atk_card: Карта, которую атакуют. Или карта, которой атакуют, если `def_card` is None.
        results: Список, в который добавляется результат.
        can_play: Может ли игрок использовать эту карту сейчас.
        theme_name: Название темы карт.
        def_card: Карта, которой бьются. Если None, то это атакующая карта.

    Adds an option representing a playing card.

    The sticker style (gray or colored) depends on whether the player can
    attack or defend with this card. The result ID is formed from the string
    representation of the card(s).

    Args:
        game: The current game object.
        atk_card: The card being attacked. Or the attacking card if `def_card` is None.
        results: The list to which the result is added.
        can_play: Whether the player can use this card now.
        theme_name: The name of the card theme.
        def_card: The defending card. If None, this is an attacking card.
    """
    card_to_show = def_card or atk_card
    is_trump = card_to_show.suit == game.trump

    # Определяем стиль стикера в зависимости от возможности хода
    # Determine sticker style based on playability
    style = 'grey'
    if can_play:
        style = 'trump_normal' if is_trump else 'normal'
    else:
        style = 'trump_grey' if is_trump else 'grey'

    sticker_id = th.get_sticker_id(repr(card_to_show), theme_name, style=style)
    if not sticker_id:
        return

    # ID должен быть уникальным для каждой комбинации атаки/защиты
    # ID must be unique for each attack/defense combination
    id_ = repr(atk_card)
    if def_card:
        id_ += f'-{repr(def_card)}'

    if can_play:
        message_text = f"⚔️ Подкинута карта: {str(atk_card)}"
        if def_card:
            message_text = f"🛡️ Побита карта {str(atk_card)} картой {str(def_card)}"

        results.append(
            Sticker(
                id=id_,
                sticker_file_id=sticker_id,
                input_message_content=InputTextMessageContent(message_text),
            )
        )
    else:
        # Если картой ходить нельзя, показываем ее серой и без возможности выбора
        # If the card cannot be played, show it as grayed out and unselectable
        results.append(
            Sticker(
                id=str(uuid4()), # Уникальный ID, чтобы избежать коллизий
                sticker_file_id=sticker_id,
                input_message_content=game_info(game) # Показываем общую инфу
            )
        )


def game_info(game: Game) -> InputTextMessageContent:
    """
    Формирует подробную информацию о текущем состоянии игры.

    Args:
        game: Текущий объект игры.

    Returns:
        Объект `InputTextMessageContent` с отформатированным текстом.

    Generates detailed information about the current game state.

    Args:
        game: The current game object.

    Returns:
        An `InputTextMessageContent` object with formatted text.
    """
    players_info = ''.join(f"\n👤 {len(pl.cards)} 🃏 | {pl.mention}" for pl in game.players)
    
    field_info = ''.join(
        f'\n  `{str(a)}` ◄- `{str(d) if d else "-"}`' 
        for a, d in game.field.items()
    )

    return InputTextMessageContent(
        message_text=(
            f"<b>🎮 Информация об игре</b>\n\n"
            f"⚔️ <b>Атакующий:</b> {game.current_player.mention} ({len(game.current_player.cards)} карт)\n"
            f"🛡️ <b>Защитник:</b> {game.opponent_player.mention} ({len(game.opponent_player.cards)} карт)\n\n"
            f"🎯 <b>Козырь:</b> {game.deck.trump_ico}\n"
            f"📦 <b>В колоде:</b> {len(game.deck.cards)} карт\n\n"
            f"<b>👥 Игроки:</b>{players_info}\n"
            f"<b>🏟️ Поле:</b>{field_info if game.field else '  (пусто)'}\n"
        ),
        parse_mode="HTML",
    )


def add_gameinfo(game: Game, results: List[InlineQueryResult], theme_name: str):
    """
    Добавляет опцию для отображения информации об игре.

    Args:
        game: Текущий объект игры.
        results: Список, в который добавляется результат.
        theme_name: Название темы карт для выбора правильного стикера.

    Adds an option to display game information.

    Args:
        game: The current game object.
        results: The list to which the result is added.
        theme_name: The name of the card theme for the correct sticker.
    """
    sticker_id = th.get_sticker_id('info', theme_name)
    if not sticker_id:
        return

    results.append(
        Sticker(
            id="gameinfo",
            sticker_file_id=sticker_id,
            input_message_content=game_info(game)
        )
    )
