# -*- coding: utf-8 -*-
"""
Модуль для обработки игровых действий.

ВАЖНО: Этот файл восстанавливает логику обработки игровых действий,
исправляя ошибки, но сохраняя оригинальную архитектуру для дальнейшего
правильного рефакторинга.

Module for handling game actions.

IMPORTANT: This file restores the game action logic, fixing errors
but preserving the original architecture for a future, correct refactoring.
"""

from aiogram import F, Router, types, Bot

# ИСПРАВЛЕНО: Убран некорректный импорт из loader.py. GameManager теперь
# будет получаться через инъекцию зависимостей.
# FIXED: Removed incorrect import from loader.py. GameManager will now
# be obtained through dependency injection.
from durak.logic import actions
from durak.logic.game_manager import GameManager
from typing import Optional
from durak.objects.card import Card
from durak.objects.game import Game
from durak.objects import GameNotFoundError, NoGameInChatError

# ИСПРАВЛЕНО: Корректный импорт GameCallback
# FIXED: Correct import for GameCallback
from .game_callback import GameCallback

router = Router()


@router.message(F.sticker)
async def process_sticker_move_handler(message: types.Message, gm: GameManager):
    """
    ОБРАБОТЧИК ХОДА КАРТОЙ ЧЕРЕЗ СТИКЕР.
    
    Извлекаем информацию о карте из стикера и вызываем игровую логику.

    STICKER CARD MOVE HANDLER.
    
    Extract card information from sticker and call game logic.
    """
    user = message.from_user
    sticker = message.sticker
    
    try:
        # ИСПОЛЬЗУЕМ get_game_by_user_id, так как игра может быть не в том же чате,
        # где была вызвана inline-клавиатура.
        game = await gm.get_game_by_user_id(user.id)
        if not game or not game.started:
            return
        
        player = game.player_for_id(user.id)
        if not player:
            return

        # Извлекаем информацию о карте из стикера
        # Используем file_unique_id для идентификации карты
        card_info = await _extract_card_from_sticker(sticker, game, user.id)
        
        # Если это не карта, а специальный стикер (draw/pass)
        if not card_info:
            await _handle_special_sticker(sticker, game, user, gm, message.bot)
            return
            
        card_str = card_info
        
        # Логика определения типа хода (атака или защита)
        if player == game.opponent_player and game.table:
            undefended_card = game.table.get_first_undefended()
            if not undefended_card:
                return
            
            def_card = Card.from_str(card_str)
            if not def_card:
                return

            # ИСПРАВЛЕНО (рефакторинг): Передаем gm и bot в функцию
            await actions.do_defence_card(game, player, undefended_card, def_card, gm, message.bot)

        elif player in (game.current_player, game.support_player):
            atk_card = Card.from_str(card_str)
            if not atk_card:
                return
            
            # ИСПРАВЛЕНО (рефакторинг): Передаем gm и bot в функцию
            await actions.do_attack_card(game, player, atk_card, gm, message.bot)

    except GameNotFoundError:
        pass
    finally:
        # Удаляем сервисное сообщение с стикером
        await message.delete()


async def _handle_special_sticker(sticker: types.Sticker, game: Game, user: types.User, gm: GameManager, bot: Bot):
    """
    Обрабатывает специальные стикеры (draw, pass).
    """
    from durak.objects import theme as th
    from durak.logic.actions import _get_attack_settings
    
    display_mode, theme_name = await _get_attack_settings(game.id)
    player = game.player_for_id(user.id)
    
    if not player:
        return
    
    # Проверяем, это стикер "draw"
    draw_sticker_id = th.get_sticker_id('draw', theme_name)
    if draw_sticker_id and sticker.file_id == draw_sticker_id:
        if player == game.opponent_player and game.table:
            await actions.do_draw(game, player, gm, bot)
        return
    
    # Проверяем, это стикер "pass"
    pass_sticker_id = th.get_sticker_id('pass', theme_name)
    if pass_sticker_id and sticker.file_id == pass_sticker_id:
        if player in (game.current_player, game.support_player):
            await actions.do_pass(game, player, gm, bot)
        return


async def _extract_card_from_sticker(sticker: types.Sticker, game: Game, user_id: int) -> Optional[str]:
    """
    Извлекает информацию о карте из стикера.
    Это сложная задача - нужно сопоставить стикер с картой.
    """
    # Временное решение: пытаемся найти карту по file_unique_id
    # В реальной реализации здесь должна быть база данных соответствий стикеров и карт
    from durak.objects import theme as th
    from durak.logic.actions import _get_attack_settings
    
    display_mode, theme_name = await _get_attack_settings(game.id)
    
    # Перебираем все карты игрока и ищем соответствующий стикер
    player = game.player_for_id(user_id)
    if not player:
        return None
        
    for card in player.cards:
        is_trump = card.suit == game.trump
        style = 'trump_normal' if is_trump else 'normal'
        sticker_id = th.get_sticker_id(repr(card), theme_name, style=style)
        if sticker_id == sticker.file_id:
            return str(card)
    
    return None


@router.message(F.text.regexp(r"^(Карта|Стікер): ([♦️♣️♥️♠️].*)$"))
async def process_card_move_handler(message: types.Message, gm: GameManager):
    """
    ОБРАБОТЧИК ХОДА КАРТОЙ (ВРЕМЕННО СОХРАНЕН).
    
    ИСПРАВЛЕНО (стабилизация):
    - Заменен несуществующий вызов `gm.get_game_by_user_id` на `gm.get_game_by_user_id`.
    
    CARD MOVE HANDLER (TEMPORARILY PRESERVED).
    
    FIXED (stabilization):
    - Replaced non-existent call `gm.get_game_by_user_id` with `gm.get_game_by_user_id`.
    """
    user = message.from_user
    card_str = message.text.split(": ", 1)[1]

    try:
        # ИСПОЛЬЗУЕМ get_game_by_user_id, так как игра может быть не в том же чате,
        # где была вызвана inline-клавиатура.
        game = await gm.get_game_by_user_id(user.id)
        if not game or not game.started:
            return
        
        player = game.player_for_id(user.id)
        if not player:
            return

        # Логика определения типа хода (атака или защита)
        if player == game.opponent_player and game.table:
            undefended_card = game.table.get_first_undefended()
            if not undefended_card:
                return
            
            def_card = Card.from_str(card_str)
            if not def_card:
                return

            # ИСПРАВЛЕНО (рефакторинг): Передаем gm и bot в функцию
            await actions.do_defence_card(game, player, undefended_card, def_card, gm, message.bot)

        elif player in (game.current_player, game.support_player):
            atk_card = Card.from_str(card_str)
            if not atk_card:
                return
            
            # ИСПРАВЛЕНО (рефакторинг): Передаем gm и bot в функцию
            await actions.do_attack_card(game, player, atk_card, gm, message.bot)

    except GameNotFoundError:
        pass
    finally:
        # Удаляем сервисное сообщение с картой
        await message.delete()
