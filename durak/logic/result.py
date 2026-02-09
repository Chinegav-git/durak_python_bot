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


def add_draw(player: Player, results: List[InlineQueryResult]):
    """Add option to draw"""
    game = player.game
    n = len(game.attacking_cards)+len(game.defending_cards)

    results.append(
        Sticker(
            id="draw", sticker_file_id=c.STICKERS['draw'],
            input_message_content=
            # InputTextMessageContent(f'Взял(а) {n} 🃏')
            InputTextMessageContent(f"🎴 {player.user.get_mention(as_html=True)} взяв(а) карти!")
        )
    )


def add_gameinfo(game: Game, results: List[InlineQueryResult]):
    """Add option to show game info"""

    results.append(
        Sticker(
            id="gameinfo",
            sticker_file_id=c.STICKERS['info'],
            input_message_content=game_info(game)
        )
    )


def add_pass(results: List[InlineQueryResult], game: Game):
    """Add option to pass"""
    results.append(
        Sticker(
            id="pass", sticker_file_id=c.STICKERS['pass'],
            input_message_content=InputTextMessageContent(
                '✅ Пас'
            )
        )
    )



def add_card(game: Game, atk_card: Card, results: List[InlineQueryResult], can_play: bool, def_card: Card = None, player: Player = None):
    """Add an option that represents a card"""

    if can_play:
        id = repr(atk_card)

        if def_card:
            id += f'-{repr(def_card)}'

            results.append(
                Sticker(id=id, sticker_file_id=c.STICKERS['normal'][repr(def_card)],
                    input_message_content=InputTextMessageContent(
                        f"🛡️ Побито карту {str(atk_card)} картою {str(def_card)}"
                    )
                )
            )

        else:
            # For attack cards that can be played, add defense button
            if not def_card:  # Only for attack cards, not defense cards
                beat = [[InlineKeyboardButton(text='⚔️ Побити цю карту!', switch_inline_query_current_chat=f'{repr(atk_card)}')]]
                results.append(
                        Sticker(id=id, sticker_file_id=c.STICKERS['normal'][repr(atk_card)],
                            input_message_content=InputTextMessageContent(
                                f"⚔️ Підкинуто карту: {str(atk_card)}"
                            )
                        )
                    )
            else:
                # Defense cards don't need buttons
                results.append(
                    Sticker(id=id, sticker_file_id=c.STICKERS['normal'][repr(def_card)],
                        input_message_content=InputTextMessageContent(
                            f"🛡️ Побито карту {str(atk_card)} картою {str(def_card)}"
                        )
                    )
                )
    
    else:
        results.append(
            Sticker(id=str(uuid4()), sticker_file_id=c.STICKERS['grey'][repr(def_card or atk_card)],
                    input_message_content=game_info(game))
        )


def game_info(game: Game):
    players = game.players
    field = game.field
    trump = game.trump
    count_cards_in_deck = len(game.deck.cards)

    pleyers_info = ''.join(f"\n👤 {len(pl.cards)} 🃏 | {pl.user.get_mention(as_html=True)}" for pl in players)
    
    field_info = ''.join(f'\n  {str(a)} ◄-- {str(d) if not d is None else "❌"}' for a, d in field.items())

    return InputTextMessageContent(
        f"<b>🎮 Інформація про гру</b>\n\n"
        f"⚔️ <b>Атакуючий:</b> {game.current_player.user.get_mention(as_html=True)} 🃏 {len(game.current_player.cards)} карт\n"
        f"🛡️ <b>Захисник:</b> {game.opponent_player.user.get_mention(as_html=True)} 🃏 {len(game.opponent_player.cards)} карт\n\n"
        f"🎯 <b>Козир:</b> {game.deck.trump_ico}\n"
        f"📦 <b>В колоді:</b> {len(game.deck.cards)} карт\n\n"
        f"<b>👥 Гравці:</b>{pleyers_info}\n"
        f"<b>🏟️ Поле:</b>\n{field_info if field else '  тут пусто~'}\n"
    )