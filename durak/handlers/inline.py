# -*- coding: utf-8 -*-
"""
Обработчики инлайн запросов для отображения карт и действий.

Handlers for inline queries to display cards and actions.
"""

from aiogram import Router, types, F
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultCachedSticker as Sticker

from durak.logic.game_manager import GameManager
from durak.logic import result
from durak.objects import NoGameInChatError, Card
from durak.objects import theme as th
from durak.utils.i18n import t

router = Router()


@router.inline_query()
async def inline_query_handler(query: types.InlineQuery, gm: GameManager):
    """
    Обрабатывает инлайн запросы для отображения карт и игровых действий.
    
    Handles inline queries for displaying cards and game actions.
    """
    user = query.from_user
    results = []  # Инициализация списка результатов
    
    try:
        game = await gm.get_game_by_user_id(user.id)
        if not game or not game.started:
            result.add_no_game(results)
            await query.answer(results, is_personal=True, cache_time=1)
            return

        player = game.player_for_id(user.id)
        if not player:
            result.add_no_game(results)
            await query.answer(results, is_personal=True, cache_time=1)
            return

        from durak.logic.actions import _get_attack_settings
        display_mode, theme_name = await _get_attack_settings(game.id)

        if not query.query:
            # Показываем только те карты, которыми игрок реально может ходить
            playable_cards = player.playable_card_atk(game)
            for card in player.cards:
                if card not in playable_cards:
                    continue

                style = 'trump_normal' if card.suit == game.trump else 'normal'
                sticker_id = th.get_sticker_id(repr(card), theme_name, style=style)
                if sticker_id:
                    # Отправляем только стикер, без текстовой команды в чат.
                    results.append(
                        Sticker(
                            id=f"attack|{repr(card)}",
                            sticker_file_id=sticker_id,
                        )
                    )

            if player == game.current_player and game.field:
                # Атакующий может нажать "Пас"
                result.add_pass(results, game, theme_name)
            elif player == game.opponent_player and game.field:
                # Защищающийся может нажать "Взять"
                result.add_draw(player, results, theme_name)

        elif query.query.startswith('beat_'):
            # Показываем карты для защиты
            atk_card_str = query.query[5:]
            atk_card = Card.from_repr(atk_card_str)

            for def_card in player.cards:
                # Используем корректную проверку возможности побить карту
                if not player.can_beat(game, atk_card, def_card):
                    continue

                style = 'trump_normal' if def_card.suit == game.trump else 'normal'
                sticker_id = th.get_sticker_id(repr(def_card), theme_name, style=style)
                if sticker_id:
                    results.append(
                        Sticker(
                            id=f"defend|{repr(atk_card)}|{repr(def_card)}",
                            sticker_file_id=sticker_id,
                        )
                    )
            # Для защищающегося также добавляем возможность "Взять"
            result.add_draw(player, results, theme_name)

    except NoGameInChatError:
        result.add_no_game(results)
    except Exception as e:
        results.append(
            InlineQueryResultArticle(
                id="error",
                title="🚫 Ошибка",
                input_message_content=InputTextMessageContent(
                    message_text=f"🚫 Произошла ошибка: {str(e)}"
                ),
            )
        )
    
    await query.answer(results, is_personal=True, cache_time=1)
