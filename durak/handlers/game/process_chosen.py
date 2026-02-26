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
    parts = result_id.split('_')
    action = parts[0]

    if action == "attack":
        card = Card.from_repr(parts[1])
        await actions.do_attack_card(game, player, card, gm, bot)
    elif action == "defend":
        atk_card = Card.from_repr(parts[1])
        def_card = Card.from_repr(parts[2])
        await actions.do_defence_card(game, player, atk_card, def_card, gm, bot)
    elif action == "pass":
        await actions.do_pass(game, player, gm, bot)
    elif action == "draw":
        await actions.do_draw(game, player, gm, bot)
