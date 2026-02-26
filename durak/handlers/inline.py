# -*- coding: utf-8 -*-
"""
Обработчики инлайн запросов для отображения карт и действий.

Handlers for inline queries to display cards and actions.
"""

from aiogram import F, Router, types
from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultCachedSticker as Sticker
)

from durak.logic import result
from durak.logic.game_manager import GameManager
from durak.objects import Card, NoGameInChatError
from durak.objects import theme as th
from durak.utils.i18n import t

router = Router()


@router.inline_query()
async def inline_query_handler(query: types.InlineQuery, gm: GameManager, l, m):
    """
    Обрабатывает все инлайн-запросы.

    В зависимости от состояния игры и ввода пользователя, этот обработчик
    формирует и отправляет список инлайн-результатов, которые могут включать:
    - Карты в руке игрока (активные и неактивные).
    - Кнопки действий (Взять, Пас).
    - Информационные сообщения (игра не найдена, игра не началась, и т.д.).

    Handles all inline queries.

    Depending on the game state and user input, this handler generates
    and sends a list of inline results, which may include:
    - Cards in the player's hand (active and inactive).
    - Action buttons (Draw, Pass).
    - Informational messages (game not found, game not started, etc.).
    """
    user = query.from_user
    results = []

    try:
        game = await gm.get_game_by_user_id(user.id)
        if not game:
            result.add_no_game(results)
            await query.answer(results, is_personal=True, cache_time=1)
            return

        if not game.started:
            result.add_not_started(results)
            await query.answer(results, is_personal=True, cache_time=1)
            return

        player = game.player_for_id(user.id)
        from durak.logic.actions import _get_attack_settings
        display_mode, theme_name = await _get_attack_settings(game.id)

        # Показываем игроку его карты и возможные действия
        # Show the player their cards and possible actions
        if player.can_play:
            if game.field: # Если на столе есть карты
                if player.is_attacker:
                    # Атакующий может подкинуть или сказать "пас"
                    for card in player.cards:
                        result.add_card(
                            game, card, results, player.can_add_card(card), theme_name
                        )
                    result.add_pass(game, results, theme_name)
                else:
                    # Защищающийся может побить или взять
                    for atk_card, def_card in game.field.items():
                        if def_card: continue
                        for card in player.cards:
                            result.add_card(
                                game, atk_card, results, player.can_beat(atk_card, card), theme_name, def_card=card
                            )
                    result.add_draw(game, player, results, theme_name)
            else:
                # Если стол пуст, атакующий может походить любой картой
                for card in player.cards:
                    result.add_card(game, card, results, True, theme_name)
        else:
            # Если не ход игрока, показываем ему серые карты и инфо
            for card in player.cards:
                result.add_card(game, card, results, False, theme_name)
            result.add_gameinfo(game, results, theme_name)

    except NoGameInChatError:
        result.add_no_game(results)
    
    except Exception as e:
        # В случае непредвиденной ошибки, сообщаем об этом пользователю
        # In case of an unexpected error, inform the user
        error_message = f"Произошла ошибка: {e}"
        results.append(InlineQueryResultArticle(
            id="error",
            title="🚫 Ошибка",
            input_message_content=InputTextMessageContent(error_message)
        ))

    await query.answer(results, is_personal=True, cache_time=1)
