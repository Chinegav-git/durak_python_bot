
import logging
from contextlib import suppress
from typing import List, Optional, Tuple

from aiogram import types
from pony.orm import db_session

from durak.objects.card import get_sticker_id, Card
from durak.objects.errors import NoGameInChatError
from loader import bot, dp, gm
from durak.db import ChatSetting
from durak.objects import Game, Player


async def get_game_and_player(user_id: int, query: types.InlineQuery) -> Tuple[Optional[Game], Optional[Player]]:
    """Gets the game and player, trying the fast path first, then falling back to a full scan."""
    # Fast path: use chat_id if available
    if query.chat_id:
        try:
            game = await gm.get_game_from_chat(query.chat_id)
            player = game.player_for_id(user_id)
            if player:
                return game, player
        except NoGameInChatError:
            # If no game in chat, fall through to the slow path, as the user might be in another game
            pass
        except Exception as e:
            logging.warning(f"Error during fast path game retrieval for chat {query.chat_id}: {e}")

    # Slow but robust path: scan all games for the user
    game_keys = await gm.redis.keys("game:*")
    for key in game_keys:
        try:
            serialized_game = await gm.redis.get(key)
            if not serialized_game:
                continue
            game = await gm._deserialize_game(serialized_game)
            player = game.player_for_id(user_id)
            if player:
                return game, player  # Found the user in a game
        except Exception as e:
            logging.warning(f"Error deserializing or checking game {key}: {e}")
            continue
            
    return None, None  # User is not in any active game


@dp.inline_handler()
async def inline_handler(query: types.InlineQuery):
    user_id = query.from_user.id
    game, player = await get_game_and_player(user_id, query)

    if not game or not player:
        await bot.answer_inline_query(
            query.id, results=[], cache_time=1,
            switch_pm_text="Не вдалося знайти вашу гру. Почніть нову!",
            switch_pm_parameter="start"
        )
        return

    if not game.started:
        await bot.answer_inline_query(query.id, results=[], cache_time=1,
                                      switch_pm_text="Гра ще не почалася. Зачекайте.",
                                      switch_pm_parameter="start")
        return

    from_card_str = query.query
    is_defending = '-' in from_card_str

    if is_defending:
        cards = _get_defending_cards(game, player, from_card_str)
        await _answer_with_cards(query, player, cards, game, from_card_str)
    else:
        cards = _get_attacking_cards(game, player)
        await _answer_with_cards(query, player, cards, game)


def _get_attacking_cards(game: Game, player: Player) -> List[Card]:
    return sorted(list(player.playable_card_atk(game)))

def _get_defending_cards(game: Game, player: Player, from_card_str: str) -> List[Card]:
    try:
        atk_card_repr = from_card_str.split('-')[0]
        atk_card = next(c for c in game.attacking_cards if repr(c) == atk_card_repr)
        return sorted(list(player.playable_card_def(game, atk_card)))
    except (StopIteration, IndexError):
        return []

@db_session
def _get_chat_card_settings(chat_id: int):
    cs = ChatSetting.get(id=chat_id)
    theme = cs.card_theme if cs else 'classic'
    mode = cs.display_mode if cs else 'text_and_sticker'
    return theme, mode

async def _answer_with_cards(query: types.InlineQuery, player: Player, cards: List[Card], game: Game, from_card_str: str = ''):
    theme, mode = _get_chat_card_settings(game.id)
    results = []
    anti_cheat_token = player.anti_cheat

    for card in cards:
        card_repr = repr(card)
        base_id = f'{from_card_str}{card_repr}' if from_card_str.endswith('-') else card_repr
        result_id = f'{base_id}:{anti_cheat_token}'

        if mode in ['text', 'text_and_sticker']:
            results.append(types.InlineQueryResultArticle(
                id=result_id,
                title=str(card),
                description=f'{card.suit.name}',
                input_message_content=types.InputTextMessageContent(f"Карта: {card}"),
                thumb_url=card.url(theme),
                thumb_width=64,
                thumb_height=64
            ))

        if mode in ['sticker', 'sticker_and_button']:
            sticker_id = get_sticker_id(card_repr, theme_name=theme, style='normal')
            if sticker_id:
                results.append(types.InlineQueryResultCachedSticker(
                    id=result_id + '_s',
                    sticker_file_id=sticker_id,
                    input_message_content=types.InputTextMessageContent(f"Стікер: {card}")
                ))

    if not cards:
        results.append(types.InlineQueryResultArticle(
            id='no_cards_to_play',
            title="Немає доступних карт",
            description="Ви не можете зробити хід.",
            input_message_content=types.InputTextMessageContent(".")
        ))

    with suppress(Exception):
        await bot.answer_inline_query(query.id, results=results, cache_time=0)
