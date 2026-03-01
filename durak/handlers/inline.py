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
async def inline_query_handler(query: types.InlineQuery, gm: GameManager):
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

        # Четко определяем роль игрока
        is_defender = player == game.opponent_player

        # Логика для защищающегося
        if is_defender and game.any_unbeaten_card:
            unbeaten_card = next((c for c, d in game.field.items() if d is None), None)
            if unbeaten_card:
                for card in player.cards:
                    # Для каждой карты в руке, проверяем, можно ли ей побить.
                    # В `add_card` передается True/False, что определяет ее стиль (активная/неактивная).
                    result.add_card(
                        game, unbeaten_card, results, player.can_beat(unbeaten_card, card), theme_name, def_card=card
                    )
            # У защищающегося всегда есть опция "Взять"
            result.add_draw(game, player, results, theme_name)
        
        # Логика для атакующих или неактивных игроков
        else:
            playable_cards = player.playable_card_atk()

            if playable_cards:  # Игрок может атаковать (основной или подкидывающий)
                for card in player.cards:
                    # Для каждой карты в руке, проверяем, можно ли ей ходить.
                    # `card in playable_cards` вернет True/False, определяя стиль.
                    result.add_card(game, card, results, card in playable_cards, theme_name)
                
                # Кнопка "Пас" доступна только основному атакующему, если раунд можно завершить
                if player == game.current_player and game.field and game.all_beaten_cards:
                    result.add_pass(game, results, theme_name)
            
            else:  # Игрок не может ходить
                for card in player.cards:
                    # Все карты отображаются как неактивные
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
            input_message_content=InputTextMessageContent(message_text=error_message)
        ))

    await query.answer(results, is_personal=True, cache_time=1)
