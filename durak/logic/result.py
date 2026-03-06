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

import html
from typing import List
from uuid import uuid4

from aiogram.types import (
    InlineQueryResult,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from ..objects import Card, Game, Player
from ..utils.i18n import I18n


def add_no_game(results: List[InlineQueryResult], l: I18n):
    """
    Добавляет сообщение о том, что пользователь не участвует в игре.
    Adds a message indicating that the user is not participating in a game.
    """
    results.append(
        InlineQueryResultArticle(
            id="nogame",
            title=l.t('inline.my_cards_title'),
            description=l.t('inline.my_cards_no_game'),
            input_message_content=InputTextMessageContent(
                message_text=l.t('game.no_game')
            ),
        )
    )


def add_not_started(results: List[InlineQueryResult], l: I18n):
    """
    Добавляет сообщение о том, что игра еще не началась.
    Adds a message indicating that the game has not yet started.
    """
    results.append(
        InlineQueryResultArticle(
            id="notstarted",
            title=l.t('inline.my_cards_title'),
            description=l.t('game.already_started'),
            input_message_content=InputTextMessageContent(
                message_text=l.t('game.already_started')
            ),
        )
    )


def add_draw(game: Game, player: Player, results: List[InlineQueryResult], theme_name: str, l: I18n):
    """
    Добавляет опцию "Взять карты" в виде статьи.
    Adds a "Draw cards" option as an article.
    """
    results.append(
        InlineQueryResultArticle(
            id="draw",
            title=l.t('game.take_action_title'),
            description=l.t('game.take_action_description'),
            input_message_content=InputTextMessageContent(
                message_text=l.t('game.take_action', name=player.name),
                parse_mode=None
            ),
        )
    )


def add_pass(game: Game, results: List[InlineQueryResult], theme_name: str, l: I18n):
    """
    Добавляет опцию "Пас" в виде статьи.
    Adds a "Pass" option as an article.
    """
    results.append(
        InlineQueryResultArticle(
            id="pass",
            title=l.t('game.pass_action_title'),
            description=l.t('game.pass_action_description'),
            input_message_content=InputTextMessageContent(
                message_text=l.t('game.pass_action'),
                parse_mode=None
            ),
        )
    )


def add_card(
    game: Game,
    atk_card: Card,
    results: List[InlineQueryResult],
    can_play: bool,
    theme_name: str,
    l: I18n,
    def_card: Card = None,
):
    """
    Добавляет опцию, представляющую собой игральную карту, в виде статьи.
    Adds an option representing a playing card as an article.
    """
    card_to_show = def_card or atk_card

    id_ = repr(atk_card)
    if def_card:
        id_ += f'-{repr(def_card)}'

    if can_play:
        if def_card:
            message_text = l.t('inline.defend_action', card=str(def_card))
            title = l.t('inline.defend_title', card=str(def_card))
            description = l.t('inline.defend_description', card=str(atk_card))
        else:
            message_text = l.t('inline.attack_action', card=str(atk_card))
            title = l.t('inline.attack_title', card=str(atk_card))
            description = l.t('inline.attack_description')
        
        results.append(
            InlineQueryResultArticle(
                id=id_,
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(
                    message_text=message_text,
                    parse_mode=None
                ),
            )
        )
    else:
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),  # Уникальный ID, чтобы избежать коллизий
                title=l.t('inline.cannot_play_title', card=str(card_to_show)),
                description=l.t('inline.cannot_play_description'),
                input_message_content=InputTextMessageContent(
                    message_text=l.t('inline.cannot_play_card'),
                    parse_mode=None
                )
            )
        )


def game_info(game: Game, l: I18n) -> InputTextMessageContent:
    """
    Формирует подробную информацию о текущем состоянии игры.
    Generates detailed information about the current game state.
    """
    players_info = ''.join(f"\n👤 <code>{len(pl.cards)}</code> 🃏 | {html.escape(pl.mention)}" for pl in game.players)
    
    field_info = ''.join(
        f'\n  <code>{str(a)}</code> ◄- <code>{str(d) if d else "❌"}</code>'
        for a, d in game.field.items()
    )

    return InputTextMessageContent(
        message_text=l.t(
            'game.info_text',
            attacker_mention=html.escape(game.current_player.mention),
            attacker_cards=len(game.current_player.cards),
            defender_mention=html.escape(game.opponent_player.mention),
            defender_cards=len(game.opponent_player.cards),
            trump_icon=game.deck.trump_ico,
            deck_size=len(game.deck.cards),
            players_info=players_info,
            field_info=field_info if game.field else l.t('game.field_empty')
        ),
        parse_mode="HTML",
    )


def add_gameinfo(game: Game, results: List[InlineQueryResult], l: I18n):
    """
    Добавляет опцию для отображения информации об игре в виде статьи.
    Это исправляет ошибку DOCUMENT_INVALID, так как Sticker не поддерживает HTML.

    Adds an option to display game information as an article.
    This fixes the DOCUMENT_INVALID error, as Sticker does not support HTML.
    """
    results.append(
        InlineQueryResultArticle(
            id="gameinfo",
            title=l.t('inline.game_info_title'),
            description=l.t('inline.game_info_description'),
            input_message_content=game_info(game, l)
        )
    )
