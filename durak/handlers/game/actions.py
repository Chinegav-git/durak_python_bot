# -*- coding: utf-8 -*-
"""
Модуль для обработки игровых действий.

Этот файл содержит основной обработчик для всех игровых действий,
которые инициируются через отправку текстовых сообщений из инлайн-режима.

Module for handling game actions.

This file contains the main handler for all game actions initiated
by sending text messages from the inline mode.
"""

from aiogram import Router, types

# ИМПОРТ: Фильтр для игровых действий.
from durak.filters.game import InGameFilter
from durak.logic import actions
from durak.logic.game_manager import GameManager
from durak.objects import GameNotFoundError
from durak.objects.card import Card
from durak.utils.i18n import I18n

router = Router()


# ИСПРАВЛЕНО: Заменен F.text на InGameFilter() для предотвращения перехвата команд.
# FIXED: Replaced F.text with InGameFilter() to prevent command interception.
@router.message(InGameFilter())
async def process_text_action_handler(message: types.Message, gm: GameManager, l: I18n):
    """
    ОБРАБОТЧИК ИГРОВЫХ ДЕЙСТВИЙ.

    Перехватывает текстовые сообщения от игроков в активной игре.
    Сравнивает их с шаблонами из локализации и вызывает игровую логику.
    
    GAME ACTION HANDLER.

    Intercepts text messages from players in an active game.
    Compares them with templates from localization and calls the game logic.
    """
    user = message.from_user
    text = message.text

    try:
        game = await gm.get_game_by_user_id(user.id)
        player = game.player_for_id(user.id)
        if not player:
            return

        # --- Определение действия по локализованному тексту ---
        # --- Determine action by localized text ---

        # 1. Действие "Пас"
        if text == l.t('game.pass_action'):
            await actions.do_pass(game, player, gm, message.bot)
        
        # 2. Действие "Взять"
        elif text == l.t('game.take_action', name=player.mention):
            await actions.do_draw(game, player, gm, message.bot)

        # 3. Действие "Атака"
        # "Атака: {card}"
        attack_prefix = l.t('inline.attack_action', card='')
        if text.startswith(attack_prefix):
            card_str = text[len(attack_prefix):]
            atk_card = Card.from_str(card_str)
            if atk_card:
                await actions.do_attack_card(game, player, atk_card, gm, message.bot)

        # 4. Действие "Защита"
        # "Защита: {card}"
        defend_prefix = l.t('inline.defend_action', card='')
        if text.startswith(defend_prefix):
            undefended_card = next((c for c, d in game.field.items() if d is None), None)
            if not undefended_card:
                return  # Нечего бить

            def_card_str = text[len(defend_prefix):]
            def_card = Card.from_str(def_card_str)
            
            if def_card:
                 await actions.do_defence_card(game, player, undefended_card, def_card, gm, message.bot)

    except (GameNotFoundError, IndexError, ValueError, KeyError):
        # Игнорируем ошибки: игра не найдена, ошибки парсинга, устаревшие сообщения, отсутствующие ключи локализации.
        # Ignore errors: game not found, parsing errors, outdated messages, missing localization keys.
        pass
    finally:
        # Шаг 3: Предотвращение падения, если у бота нет прав на удаление.
        # Step 3: Prevent crash if the bot lacks permission to delete.
        try:
            await message.delete()
        except Exception:
            pass  # Игнорируем ошибку, если не удалось удалить сообщение.
