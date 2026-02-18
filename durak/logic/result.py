from aiogram import types
from aiogram.types import InlineQueryResultArticle, InlineQueryResult, \
                    InlineQueryResultCachedSticker as Sticker, \
                    InputTextMessageContent, InlineKeyboardButton, \
                    InlineKeyboardMarkup
from typing import List
from uuid import uuid4
from config import Commands

from ..objects import Player, Game, Card, card as c


def add_no_game(results: List[InlineQueryResult]):
    """Add text result if user is not playing"""
    results.append(
        InlineQueryResultArticle(
            id="nogame",
            title = "🎮 Ви не граєте",
            input_message_content=
            InputTextMessageContent('🚫 Ви зараз не граєте. Використовуйте /new щоб '
                                    'почати гру або /join, щоб приєднатися до гри '
                                    'поточна гра в цій групі')
        )
    )


def add_not_started(results: List[InlineQueryResult]):
    """Add text result if the game has not yet started"""
    results.append(
        InlineQueryResultArticle(
            id="nogame",
            title = "⏳ Гра ще не почалася",
            input_message_content=
            InputTextMessageContent(f'🚀 Запустити гру /{Commands.START}')
        )
    )


def add_draw(game: Game, player: Player, results: List[InlineQueryResult], theme_name: str):
    """Add option to draw"""
    sticker_id = c.get_sticker_id('draw', theme_name)
    if not sticker_id:
        return # Or add a default text representation

    results.append(
        Sticker(
            id="draw", sticker_file_id=sticker_id,
            input_message_content=
            InputTextMessageContent(f"🎴 {player.mention} взяв(ла) карти!")
        )
    )


def add_gameinfo(game: Game, results: List[InlineQueryResult], theme_name: str):
    """Add option to show game info"""
    sticker_id = c.get_sticker_id('info', theme_name)
    if not sticker_id:
        return

    results.append(
        Sticker(
            id="gameinfo",
            sticker_file_id=sticker_id,
            input_message_content=game_info(game)
        )
    )


def add_pass(results: List[InlineQueryResult], game: Game, theme_name: str):
    """Add option to pass"""
    sticker_id = c.get_sticker_id('pass', theme_name)
    if not sticker_id:
        return

    results.append(
        Sticker(
            id="pass", sticker_file_id=sticker_id,
            input_message_content=InputTextMessageContent(
                '✅ Пас'
            )
        )
    )


def add_card(game: Game, atk_card: Card, results: List[InlineQueryResult], can_play: bool, theme_name: str, def_card: Card = None, player: Player = None):
    """Add an option that represents a card"""
    card_to_show = def_card or atk_card
    is_trump = card_to_show.suit == game.trump

    style = 'grey'
    if can_play:
        style = 'trump_normal' if is_trump else 'normal'
    else:
        style = 'trump_grey' if is_trump else 'grey'

    sticker_id = c.get_sticker_id(repr(card_to_show), theme_name, style=style)
    if not sticker_id:
        # Fallback or log error if a card sticker is missing
        return

    id_ = repr(atk_card)
    if def_card:
        id_ += f'-{repr(def_card)}'

    if can_play:
        if def_card:
            results.append(
                Sticker(id=id_, sticker_file_id=sticker_id,
                    input_message_content=InputTextMessageContent(
                        f"🛡️ Побито карту {str(atk_card)} картою {str(def_card)}"
                    )
                )
            )
        else:
            results.append(
                Sticker(id=id_, sticker_file_id=sticker_id,
                    input_message_content=InputTextMessageContent(
                        f"⚔️ Підкинуто карту: {str(atk_card)}"
                    )
                )
            )
    else:
        results.append(
            Sticker(id=str(uuid4()), sticker_file_id=sticker_id,
                    input_message_content=game_info(game))
        )


def game_info(game: Game):
    players = game.players
    field = game.field
    trump = game.trump
    count_cards_in_deck = len(game.deck.cards)

    pleyers_info = ''.join(f"\n👤 {len(pl.cards)} 🃏 | {pl.mention}" for pl in players)
    
    field_info = ''.join(f'\n  {str(a)} ◄-- {str(d) if not d is None else "❌"}' for a, d in field.items())

    return InputTextMessageContent(
        f"<b>🎮 Інформація про гру</b>\n\n"
        f"⚔️ <b>Атакуючий:</b> {game.current_player.mention} 🃏 {len(game.current_player.cards)} карт\n"
        f"🛡️ <b>Захисник:</b> {game.opponent_player.mention} 🃏 {len(game.opponent_player.cards)} карт\n\n"
        f"🎯 <b>Козир:</b> {game.deck.trump_ico}\n"
        f"📦 <b>В колоді:</b> {len(game.deck.cards)} карт\n\n"
        f"<b>👥 Гравці:</b>{pleyers_info}\n"
        f"<b>🏟️ Поле:</b>\n{field_info if field else '  тут пусто~'}\n"
    )
