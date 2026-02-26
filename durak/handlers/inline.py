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
        # Показываем карты игрока при пустом запросе (нажатие кнопки "Мои карты")
        if not query.query:
            # Получаем игру пользователя
            game = await gm.get_game_by_user_id(user.id)
            if not game:
                result.add_no_game(results)
                return
            
            # Проверяем, начата ли игра
            if not game.started:
                result.add_not_started(results)
                return
            
            # Получаем игрока
            player = game.player_for_id(user.id)
            if not player:
                result.add_no_game(results)
                return
            
            # Получаем настройки чата
            from durak.logic.actions import _get_attack_settings
            display_mode, theme_name = await _get_attack_settings(game.id)
            
            # Добавляем все карты игрока
            for card in player.cards:
                # Для отображения в руке все карты показываем как стикеры
                is_trump = card.suit == game.trump
                style = 'trump_normal' if is_trump else 'normal'
                sticker_id = th.get_sticker_id(repr(card), theme_name, style=style)
                if sticker_id:
                    results.append(
                        Sticker(
                            id=f"hand_{repr(card)}",
                            sticker_file_id=sticker_id,
                            input_message_content=InputTextMessageContent(
                                message_text=f"Карта: {str(card)}"
                            ),
                        )
                    )
            
            # Добавляем опции "Взять" и "Пас" в зависимости от ситуации
            if player == game.opponent_player and game.table:
                # Защищающийся игрок может взять карты
                result.add_draw(game, player, results, theme_name)
            elif player in (game.current_player, game.support_player):
                # Атакующий игрок может сказать пас
                result.add_pass(game, player, results, theme_name)
        
        elif query.query.startswith('beat_'):
            # Обработка запросов для побития карты - показываем только карты для выбора
            card_str = query.query[5:]  # Убираем префикс 'beat_'
            game = await gm.get_game_by_user_id(user.id)
            if not game:
                result.add_no_game(results)
                return
            
            # Проверяем, начата ли игра
            if not game.started:
                result.add_not_started(results)
                return
            
            # Получаем игрока
            player = game.player_for_id(user.id)
            if not player or player != game.opponent_player:
                result.add_no_game(results)
                return
            
            # Получаем настройки чата
            from durak.logic.actions import _get_attack_settings
            display_mode, theme_name = await _get_attack_settings(game.id)
            
            # Показываем все карты игрока для выбора
            for def_card in player.cards:
                is_trump = def_card.suit == game.trump
                style = 'trump_normal' if is_trump else 'normal'
                sticker_id = th.get_sticker_id(repr(def_card), theme_name, style=style)
                if sticker_id:
                    results.append(
                        Sticker(
                            id=f"def_{repr(def_card)}",
                            sticker_file_id=sticker_id,
                            input_message_content=InputTextMessageContent(
                                message_text=f"Карта: {str(def_card)}"
                            ),
                        )
                    )
            
            # Добавляем опции "Взять" и "Пас" для защитника
            result.add_draw(game, player, results, theme_name)
            result.add_pass(game, player, results, theme_name)
            
    except NoGameInChatError:
        result.add_no_game(results)
    except Exception as e:
        # В случае ошибки добавляем сообщение об ошибке
        results.append(
            InlineQueryResultArticle(
                id="error",
                title="🚫 Ошибка",
                input_message_content=InputTextMessageContent(
                    message_text=f"🚫 Произошла ошибка: {str(e)}"
                ),
            )
        )
    
    # Отправляем результаты инлайн запроса
    await query.answer(results, is_personal=True, cache_time=1)
