# -*- coding: utf-8 -*-
"""
Модуль для генерации результатов инлайн-режима.

Этот модуль отвечает за преобразование текущего состояния игры (Game, Player)
в список объектов `InlineQueryResult`, которые Telegram отображает пользователю
в виде подсказок над полем ввода. Каждый результат представляет собой возможное
действие (например, походить картой, взять, пас) или информационное сообщение.

-------------------------------------------------------------------------------

Module for generating inline mode results.

This module is responsible for converting the current game state (Game, Player)
into a list of `InlineQueryResult` objects, which Telegram displays to the user
as suggestions above the input field. Each result represents a possible
action (e.g., play a card, draw, pass) or an informational message.
"""

from typing import List
from uuid import uuid4

from aiogram.types import (
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
    Adds a message indicating that the user is not participating in a game.
    """
    results.append(
        InlineQueryResultArticle(
            id="nogame",
            title="🎮 Вы не играете",
            input_message_content=InputTextMessageContent(
                message_text='🚫 Вы сейчас не играете. Используйте /new чтобы '
                'начать игру или /join, чтобы присоединиться к '
                'текущей игре в этой группе',
                parse_mode="HTML"
            ),
        )
    )


def add_not_started(results: List[InlineQueryResult]):
    """
    Добавляет сообщение о том, что игра еще не началась.
    Adds a message indicating that the game has not yet started.
    """
    results.append(
        InlineQueryResultArticle(
            id="notstarted",
            title="⏳ Игра еще не началась",
            input_message_content=InputTextMessageContent(
                message_text=f'🚀 Начать игру: /{Commands.START}',
                parse_mode="HTML"
            ),
        )
    )


def add_draw(game: Game, player: Player, results: List[InlineQueryResult], theme_name: str):
    """
    Добавляет опцию "Взять карты" в виде стикера.
    Adds a "Draw cards" option as a sticker.
    """
    sticker_id = th.get_sticker_id('draw', theme_name)
    if not sticker_id:
        return

    results.append(
        Sticker(
            id="draw",
            sticker_file_id=sticker_id,
            input_message_content=InputTextMessageContent(
                message_text=f"🎴 {player.mention} взял(а) карты!",
                parse_mode="HTML"
            ),
        )
    )


def add_pass(game: Game, results: List[InlineQueryResult], theme_name: str):
    """
    Добавляет опцию "Пас" в виде стикера.
    Adds a "Pass" option as a sticker.
    """
    sticker_id = th.get_sticker_id('pass', theme_name)
    if not sticker_id:
        return

    results.append(
        Sticker(
            id="pass",
            sticker_file_id=sticker_id,
            input_message_content=InputTextMessageContent(
                message_text='✅ Пас',
                parse_mode="HTML"
            ),
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
    Adds an option representing a playing card.
    """
    card_to_show = def_card or atk_card
    is_trump = card_to_show.suit == game.trump

    style = 'grey'
    if can_play:
        style = 'trump_normal' if is_trump else 'normal'
    else:
        style = 'trump_grey' if is_trump else 'grey'

    sticker_id = th.get_sticker_id(repr(card_to_show), theme_name, style=style)
    if not sticker_id:
        return

    id_ = repr(atk_card)
    if def_card:
        id_ += f'-{repr(def_card)}'

    if can_play:
        if def_card:
            message_text = f"🛡️ Побито карту {str(atk_card)} картой {str(def_card)}"
        else:
            message_text = f"⚔️ Подкинуто карту: {str(atk_card)}"

        results.append(
            Sticker(
                id=id_,
                sticker_file_id=sticker_id,
                input_message_content=InputTextMessageContent(
                    message_text=message_text,
                    parse_mode="HTML"
                ),
            )
        )
    else:
        results.append(
            Sticker(
                id=str(uuid4()),  # Уникальный ID, чтобы избежать коллизий
                sticker_file_id=sticker_id,
                input_message_content=game_info(game)  # Показываем общую инфу
            )
        )


def game_info(game: Game) -> InputTextMessageContent:
    """
    Формирует подробную информацию о текущем состоянии игры.
    Generates detailed information about the current game state.
    """
    players_info = ''.join(f"\n👤 {len(pl.cards)} 🃏 | {pl.mention}" for pl in game.players)
    
    field_info = ''.join(
        f'\n  `{str(a)}` ◄- `{str(d) if d else "❌"}`'
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
    Adds an option to display game information.
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