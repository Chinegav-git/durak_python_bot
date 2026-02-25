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

from aiogram import F, Router, types

# ИСПРАВЛЕНО: Убран некорректный импорт из loader.py. GameManager теперь
# будет получаться через инъекцию зависимостей.
# FIXED: Removed incorrect import from loader.py. GameManager will now
# be obtained through dependency injection.
from durak.logic import actions
from durak.logic.game_manager import GameManager
from durak.objects.card import Card
from durak.objects import GameNotFoundError, NoGameInChatError

# ИСПРАВЛЕНО: Корректный импорт GameCallback
# FIXED: Correct import for GameCallback
from .game_callback import GameCallback

router = Router()


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

            # ИСПРАВЛЕНО (рефакторинг): Передаем gm в функцию
            await actions.do_defence_card(game, player, undefended_card, def_card, gm)

        elif player in (game.current_player, game.support_player):
            atk_card = Card.from_str(card_str)
            if not atk_card:
                return
            
            # ИСПРАВЛЕНО (рефакторинг): Передаем gm в функцию
            await actions.do_attack_card(game, player, atk_card, gm)

    except GameNotFoundError:
        pass
    finally:
        # Удаляем сервисное сообщение с картой
        await message.delete()


@router.callback_query(GameCallback.filter(F.action == "take"))
async def take_cards_callback_handler(call: types.CallbackQuery, callback_data: GameCallback, gm: GameManager):
    """
    Обрабатывает нажатие на кнопку "Взять".
    
    ИСПРАВЛЕНО (стабилизация):
    - Заменен неверный вызов `gm.get_game` на `gm.get_game_from_chat`.
    
    Handles the "Take" button press.

    FIXED (stabilization):
    - Replaced incorrect call `gm.get_game` with `gm.get_game_from_chat`.
    """
    try:
        game = await gm.get_game_from_chat(int(callback_data.game_id))
        player = game.player_for_id(call.from_user.id)

        if not player or player != game.opponent_player:
            await call.answer("Лише захисаючий гравець може взяти карти.", show_alert=True)
            return

        # ИСПРАВЛЕНО (рефакторинг): Передаем gm в функцию
        await actions.do_draw(game, player, gm)
        await call.answer("Ви взяли карти зі стола.")
    
    except (NoGameInChatError, ValueError):
        await call.answer("Гру не знайдено або вже завершена.", show_alert=True)


@router.callback_query(GameCallback.filter(F.action == "pass"))
async def pass_turn_callback_handler(call: types.CallbackQuery, callback_data: GameCallback, gm: GameManager):
    """
    Обрабатывает нажатие на кнопку "Пас" (бито).
    
    ИСПРАВЛЕНО (стабилизация):
    - Заменен неверный вызов `gm.get_game` на `gm.get_game_from_chat`.

    Handles the "Pass" (bito) button press.

    FIXED (stabilization):
    - Replaced incorrect call `gm.get_game` with `gm.get_game_from_chat`.
    """
    try:
        game = await gm.get_game_from_chat(int(callback_data.game_id))
        player = game.player_for_id(call.from_user.id)

        if not player or player not in (game.current_player, game.support_player):
            await call.answer("Зараз не ваш хід, щоб пасувати.", show_alert=True)
            return
        
        # ИСПРАВЛЕНО (рефакторинг): Передаем gm и bot в функцию
        await actions.do_pass(game, player, gm, call.bot)
        await call.answer("Пас!")
            
    except (NoGameInChatError, ValueError):
        await call.answer("Гру не знайдено або вже завершена.", show_alert=True)
