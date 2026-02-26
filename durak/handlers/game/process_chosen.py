# -*- coding: utf-8 -*-
"""
Обработчик выбора в инлайн-режиме (когда игрок нажимает на карту).

Handler for inline mode selection (when a player clicks on a card).
"""
import logging

from aiogram import Bot, F, Router, types

from durak.logic import actions
from durak.logic.game_manager import GameManager
from durak.objects import Card, NoGameInChatError, Player

logger = logging.getLogger(__name__)

router = Router()


@router.chosen_inline_result()
async def chosen_inline_result_handler(
    query: types.ChosenInlineResult, gm: GameManager, bot: Bot
):
    """
    Обрабатывает выбор, сделанный игроком в инлайн-режиме.
    
    Handles the selection made by a player in inline mode.
    """
    user = query.from_user
    try:
        game = await gm.get_game_by_user_id(user.id)
    except NoGameInChatError:
        return

    player = game.player_for_id(user.id)
    if not player:
        return

    result_id = query.result_id

    # Идентификатор результата кодирует действие и данные.
    # Новый формат: "attack|14_h", "defend|14_h|6_c"
    # Старый формат (совместимость): "attack_14h", "defend_14h_6c"
    sep = '|' if '|' in result_id else '_'
    parts = result_id.split(sep)
    action = parts[0]

    if action == "attack":
        # После первого разделителя всё остальное — строковое представление карты.
        card_repr = sep.join(parts[1:])
        card = Card.from_repr(card_repr)
        await actions.do_attack_card(game, player, card, gm, bot)
    elif action == "defend":
        payload = parts[1:]
        if sep == '|' and len(payload) == 2:
            atk_repr, def_repr = payload
        else:
            # Фолбэк для старого формата: пытаемся разделить поровну.
            mid = len(payload) // 2 or 1
            atk_repr = sep.join(payload[:mid])
            def_repr = sep.join(payload[mid:])
        atk_card = Card.from_repr(atk_repr)
        def_card = Card.from_repr(def_repr)
        await actions.do_defence_card(game, player, atk_card, def_card, gm, bot)
    elif action == "pass":
        await actions.do_pass(game, player, gm, bot)
    elif action == "draw":
        await actions.do_draw(game, player, gm, bot)
