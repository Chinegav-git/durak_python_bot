# -*- coding: utf-8 -*-
"""
Обработчики инлайн запросов для отображения карт и действий.

Handlers for inline queries to display cards and actions.
"""

from aiogram import Router, types

# ИСПРАВЛЕНО: Добавлены импорты для получения настроек чата.
# FIXED: Added imports to get chat settings.
from durak.db.models import Chat, ChatSetting
from durak.logic import result
from durak.logic.game_manager import GameManager
from durak.objects import NoGameInChatError

router = Router()


# ИСПРАВЛЕНО: Убран аргумент `m`, так как он не передавался через middleware.
# FIXED: Removed the `m` argument as it was not being passed via middleware.
@router.inline_query()
async def inline_query_handler(query: types.InlineQuery, gm: GameManager, l):
    """
    Обрабатывает все инлайн-запросы. Финальная двухуровневая логика.

    Handles all inline queries. Final two-block logic.
    """
    user = query.from_user
    results = []

    try:
        game = await gm.get_game_by_user_id(user.id)
        if not game or not game.started:
            result.add_no_game(results)
            await query.answer(results, is_personal=True, cache_time=0)
            return

        # ИСПРАВЛЕНО: Настройки чата (включая тему) получаются вручную.
        # FIXED: Chat settings (including the theme) are retrieved manually.
        # ИСПРАВЛЕНО: Использован `game.id` вместо `game.chat_id` для получения ID чата.
        # FIXED: Used `game.id` instead of `game.chat_id` to get the chat ID.
        chat, _ = await Chat.get_or_create(id=game.id)
        chat_settings, _ = await ChatSetting.get_or_create(chat=chat)

        player = game.player_for_id(user.id)
        theme_name = chat_settings.theme

        is_defender = player == game.opponent_player
        is_attacker = player == game.current_player

        # --- Блок 1: Логика для ЗАЩИЩАЮЩЕГОСЯ --- #
        # Срабатывает, если игрок - защитник и на поле есть что бить.
        if is_defender and game.any_unbeaten_card:
            unbeaten_card = next((c for c, d in game.field.items() if d is None), None)
            if unbeaten_card:
                for card in player.cards:
                    # Показываем, какими картами можно побить атакующую.
                    result.add_card(
                        game, unbeaten_card, results,
                        player.can_beat(unbeaten_card, card),
                        theme_name, def_card=card
                    )
            # У защищающегося всегда есть опция "Взять".
            result.add_draw(game, player, results, theme_name)

        # --- Блок 2: Логика для ВСЕХ ОСТАЛЬНЫХ (атака, подкидывание, ожидание) --- #
        else:
            # Ключевая логика: возможность хода определяется методом playable_card_atk().
            # Он вернет пустой список, если ходить/подкидывать нельзя.
            playable_cards = player.playable_card_atk()

            for card in player.cards:
                # Карты активны, только если они есть в списке доступных для хода.
                result.add_card(game, card, results, card in playable_cards, theme_name)
            
            # Стикер "Пас" виден ТОЛЬКО главному атакующему.
            if is_attacker:
                result.add_pass(game, results, theme_name)

            # Стикер "Инфо" виден всем, кто не защищается.
            result.add_gameinfo(game, results, theme_name)

    except NoGameInChatError:
        result.add_no_game(results)
    
    except Exception as e:
        results.append(types.InlineQueryResultArticle(
            id="error",
            title=f"🚫 Ошибка: {e}",
            input_message_content=types.InputTextMessageContent(message_text=f"Произошла непредвиденная ошибка: {e}")
        ))

    await query.answer(results, is_personal=True, cache_time=0)
