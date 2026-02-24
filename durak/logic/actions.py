# -*- coding: utf-8 -*-
"""
Модуль игровых действий (контроллер).

Этот модуль является связующим звеном между обработчиками команд Telegram (`handlers`)
и ядром игровой логики (`objects`). Он содержит `async` функции, которые
оркестрируют игровой процесс: управляют ходами, обрабатывают действия игроков
(атака, защита, пас, взять карты), отправляют уведомления в чат и обновляют
состояние игры через GameManager.

Все функции здесь принимают объект `Game` и `Player` и выполняют определенное
игровое действие, производя необходимые сайд-эффекты (отправка сообщений, 
сохранение состояния).

-------------------------------------------------------------------------------------

Game actions module (controller).

This module acts as the link between Telegram command handlers (`handlers`)
and the core game logic (`objects`). It contains `async` functions that
orchestrate the gameplay: managing turns, handling player actions
(attack, defense, pass, draw cards), sending notifications to the chat, and updating
the game state via the GameManager.

All functions here take a `Game` and `Player` object and perform a specific
game action, producing the necessary side effects (sending messages,
saving state).
"""

import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ИСПРАВЛЕНО (рефакторинг): Удален импорт `CHOISE` и `gm` из устаревшего модуля `loader`.
# # Глобальный GameManager <-- Старый комментарий сохранен для истории.
# Зависимость GameManager теперь внедряется через аргументы функций.
# FIXED (refactoring): Removed `CHOISE` and `gm` import from the deprecated `loader` module.
# # Global GameManager <-- Old comment saved for history.
# The GameManager dependency is now injected via function arguments.
from ..db.models import ChatSetting, UserSetting # ИСПРАВЛЕНО: Убран неиспользуемый UserSetting
from ..handlers.game.game_callback import GameCallback
from ..logic.game_manager import GameManager
from ..objects import Card, Game, Player
# ИСПРАВЛЕНО: `card as c` заменен на `theme as th` для получения стикеров
from ..objects import theme as th
from ..objects.errors import NoGameInChatError, NotAllowedMove

logger = logging.getLogger(__name__)


async def _delete_message_after_delay(chat_id: int, message_id: int, delay: int):
    """
    Асинхронно удаляет сообщение через указанное количество секунд.
    Используется для удаления временных уведомлений (например, "пас").
    
    Asynchronously deletes a message after a specified number of seconds.
    Used for deleting temporary notifications (e.g., "pass").
    """
    await asyncio.sleep(delay)
    try:
        await Bot.get_current().delete_message(chat_id, message_id)
    except Exception:
        # Ошибки игнорируются, так как сообщение могло быть уже удалено
        # Errors are ignored, as the message might have already been deleted
        pass


async def send_turn_notification(game: Game):
    """
    Отправляет в чат уведомление о смене хода.
    
    Sends a turn change notification to the chat.
    """
    bot = Bot.get_current()
    attacker = game.current_player
    defender = game.opponent_player
    if not defender:
        return

    # ИСПРАВЛЕНО (рефакторинг): Клавиатура-заглушка CHOISE заменена на динамическую
    # с использованием InlineKeyboardBuilder и GameCallback для консистентности.
    # FIXED (refactoring): The CHOISE placeholder keyboard has been replaced with a dynamic one
    # using InlineKeyboardBuilder and GameCallback for consistency.
    builder = InlineKeyboardBuilder()
    builder.button(text="🃏 Мои карты", callback_data=GameCallback(action="my_cards", game_id=str(game.id)).pack())
    builder.button(text="✅ Пас", callback_data=GameCallback(action="pass", game_id=str(game.id)).pack())
    builder.button(text="📥 Взять", callback_data=GameCallback(action="take", game_id=str(game.id)).pack())
    builder.adjust(1, 2)

    text = (
        f'✅ <b>Переход хода</b>\n\n'
        f'⚔️ Атакует: {attacker.mention} (🃏{len(attacker.cards)})\n'
        f'🛡️ Защищается: {defender.mention} (🃏{len(defender.cards)})\n\n'
        f'🃏 Козырь: {game.deck.trump_ico}\n'
        f'🃏 В колоде: {len(game.deck.cards)} карт'
    )
    await bot.send_message(game.id, text, reply_markup=builder.as_markup())


async def send_no_more_attacks_notification(game: Game):
    """
    Отправляет уведомление о том, что защитник отбился и больше подкидывать нельзя.

    Sends a notification that the defender has successfully defended and no more attacks are allowed.
    """
    bot = Bot.get_current()
    defender = game.opponent_player
    if not defender or not game.round_attackers:
        return

    # Собираем всех, кто атаковал в этом раунде
    main_attacker = game.round_attackers[0]
    support_attackers = list(set(game.round_attackers[1:]))

    text = f"🛡️ {defender.mention} отбил(а) все карты.\n🔄 Больше подкидывать нельзя.\n\n⚔️ Атаковал(а): {main_attacker.mention}"
    if support_attackers:
        support_mentions = ', '.join([p.mention for p in support_attackers])
        text += f"\n↪️ Подкидывал(и): {support_mentions}"

    msg = await bot.send_message(game.id, text)
    if msg:
        # Удаляем это сообщение через 10 секунд
        asyncio.create_task(_delete_message_after_delay(msg.chat.id, msg.message_id, 10))

#
# ИСПРАВЛЕНО: Функционал статистики временно удален, так как он был основан
# на устаревшей и нерабочей модели UserSetting. Его нужно будет переписать с нуля.
#
# async def _update_win_stats(user_id: int): ...

async def win(game: Game, player: Player, gm: GameManager):
    """
    Обрабатывает победу игрока. Отправляет сообщение и сохраняет победителя.

    Handles a player's victory. Sends a message and saves the winner.
    """
    # await _update_win_stats(player.id) # Статистика временно отключена
    
    if not hasattr(game, 'winners'):
        game.winners = []

    if player not in game.winners:
        bot = Bot.get_current()
        if not game.winner:
            game.winner = player
            await bot.send_message(game.id, f'🏆 {player.mention} - победитель!')
        else:
            # Последующие игроки, у которых кончились карты
            await bot.send_message(game.id, f'🎉 {player.mention} - тоже побеждает!')
        game.winners.append(player)
    
    await gm.save_game(game)


async def do_turn(game: Game, gm: GameManager, skip_def: bool = False):
    """
    Выполняет переход хода. Проверяет, не окончена ли игра или не вышел ли кто-то.
    Если игра окончена, отправляет итоговое сообщение. В противном случае - передает ход.
    
    Executes a turn transition. Checks if the game is over or if someone has left.
    If the game is over, sends the final message. Otherwise, passes the turn.
    """
    while True:
        # 1. Проверка на завершение игры
        if game.game_is_over:
            with suppress(NoGameInChatError):
                if await gm.get_game_from_chat(game.id):
                    final_text = gm.get_game_end_message(game)
                    await gm.end_game(game)
                    await Bot.get_current().send_message(game.id, final_text, reply_markup=types.ReplyKeyboardRemove())
            return

        # 2. Проверка, не вышли ли игроки (если у них кончились карты)
        player_has_left = False
        for player in list(game.players):
            if not player.cards and not player.finished_game:
                await win(game, player, gm)
                player.finished_game = True
                player_has_left = True

        if player_has_left:
            continue  # Повторяем цикл, чтобы проверить, не закончилась ли игра
        else:
            break  # Все на месте, выходим из цикла

    # 3. Передаем ход и сохраняем состояние
    game.turn(skip_def=skip_def)
    await gm.save_game(game)

    # 4. Уведомляем игроков о новом ходе
    if not skip_def:
        await send_turn_notification(game)


async def do_leave_player(game: Game, player: Player, gm: GameManager, from_turn: bool = False):
    """
    Обрабатывает выход игрока из игры.
    
    Processes a player leaving the game.
    """
    await gm.leave_game(game, player)

    if not game.started:
        return

    if not from_turn:
        was_defender = (game.opponent_player and player.id == game.opponent_player.id)
        await do_turn(game, gm, skip_def=was_defender)


async def do_pass(game: Game, player: Player, gm: GameManager):
    """
    Обрабатывает действие "Пас" от атакующего игрока.
    
    Handles the "Pass" action from an attacking player.
    """
    if player != game.current_player:
        return

    game.is_pass = True
    await gm.save_game(game)
    
    bot = Bot.get_current()
    msg = await bot.send_message(game.id, f"Пас! {player.mention} больше не подкидывает в этом раунде.")
    if msg:
        asyncio.create_task(_delete_message_after_delay(msg.chat.id, msg.message_id, 7))

    # Если все карты на поле побиты, и кто-то сказал "пас", ход завершается
    if game.all_beaten_cards:
        await do_turn(game, gm)


async def do_draw(game: Game, player: Player, gm: GameManager):
    """
    Обрабатывает действие "Взять" от защищающегося игрока.
    Игрок забирает все карты с поля, и ход остается у атакующих.
    
    Handles the "Draw" action from the defending player.
    The player takes all cards from the field, and the turn remains with the attackers.
    """
    if not game.opponent_player or player.id != game.opponent_player.id:
        return

    bot = Bot.get_current()

    # Удаляем старые сообщения-кнопки и стикеры карт
    for msg_id in list(game.attack_announce_message_ids.values()):
        with suppress(Exception): await bot.delete_message(game.id, msg_id)
    game.attack_announce_message_ids.clear()

    for sticker_id in list(game.attack_sticker_message_ids.values()):
        with suppress(Exception): await bot.delete_message(game.id, sticker_id)
    game.attack_sticker_message_ids.clear()
    
    taking_player = game.opponent_player
    game.take_all_field() # Ключевая логика - игрок берет карты
    await do_turn(game, gm, skip_def=True) # Переход хода без смены защитника

    attacker = game.current_player
    defender = game.opponent_player
    
    # Уведомление о том, что игрок взял карты
    builder = InlineKeyboardBuilder()
    builder.button(text="🃏 Мои карты", callback_data=GameCallback(action="my_cards", game_id=str(game.id)).pack())
    builder.button(text="✅ Пас", callback_data=GameCallback(action="pass", game_id=str(game.id)).pack())
    builder.button(text="📥 Взять", callback_data=GameCallback(action="take", game_id=str(game.id)).pack())
    builder.adjust(1, 2)
    
    text = (
        f'↪️ <b>Ход остается</b>\n\n'
        f'🫳 {taking_player.mention} берет карты.\n'
        f'⚔️ Атакует: {attacker.mention} (🃏{len(attacker.cards)})\n'
        f'🛡️ Защищается: {defender.mention} (🃏{len(defender.cards)})\n\n'
        f'🃏 Козырь: {game.deck.trump_ico}\n'
        f'🃏 В колоде: {len(game.deck.cards)} карт'
    )
    await bot.send_message(game.id, text, reply_markup=builder.as_markup())


async def _get_attack_settings(chat_id: int):
    """
    Получает настройки чата, необходимые для атаки (режим отображения, тема карт).
    ИСПРАВЛЕНО: Удалена нерабочая логика статистики.

    Gets the chat settings required for an attack (display mode, card theme).
    FIXED: Removed non-functional statistics logic.
    """
    cs, _ = await ChatSetting.get_or_create(chat_id=chat_id)
    return cs.game_mode, cs.card_theme


async def _update_attack_stats(user_id: int):
    """
    Обновляет статистику атаки для пользователя.
    Updates attack statistics for a user.
    """
    us, _ = await UserSetting.get_or_create(user_id=user_id)
    if us.stats_enabled:
        us.cards_played += 1
        us.cards_attack += 1
        await us.save()


async def do_attack_card(game: Game, player: Player, card: Card, gm: GameManager):
    """
    Обрабатывает ход атакующей картой.
    
    Handles an attacking card move.
    """
    try:
        player.play_attack(game, card)
    except NotAllowedMove as e:
        logger.warning(f"Игрок {player.id} попытался сделать некорректный ход: {e}")
        return

    # Обновляем статистику
    await _update_attack_stats(player.id)

    bot = Bot.get_current()
    display_mode, theme_name = await _get_attack_settings(game.id)

    # Если это был основной атакующий, сбрасываем флаг "пас"
    if player == game.current_player:
        game.is_pass = False

    if player not in game.round_attackers:
        game.round_attackers.append(player)

    # Финальный раунд (когда у игрока кончились карты, а в колоде пусто)
    if not player.cards and len(game.players) <= 2 and not game.deck.cards:
        game.is_final = True

    await gm.save_game(game)

    beat_markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='🛡️ Побить эту карту!', switch_inline_query_current_chat=f'{repr(card)}')]
    ])

    # В зависимости от настроек чата, отправляем стикер, текст или и то и другое
    sticker_msg = None
    if display_mode in ['text_and_sticker', 'sticker_and_button']:
        style = 'trump_normal' if card.suit == game.trump else 'normal'
        sticker_id = th.get_sticker_id(repr(card), theme_name=theme_name, style=style)
        if sticker_id:
            try:
                sticker_msg = await bot.send_sticker(game.id, sticker_id, reply_markup=beat_markup if display_mode == 'sticker_and_button' else None)
                if sticker_msg:
                    game.attack_sticker_message_ids[card] = sticker_msg.message_id
                    await gm.save_game(game)
            except Exception:
                pass

    if not (display_mode == 'sticker_and_button' and sticker_msg):
        text = f"⚔️ <b>{player.mention}</b> подкинул(а) карту: {str(card)}\n🛡️ для {game.opponent_player.mention}"
        msg = await bot.send_message(game.id, text, reply_markup=beat_markup)
        if msg:
            game.attack_announce_message_ids[card] = msg.message_id
            await gm.save_game(game)

#
# ИСПРАВЛЕНО: Функционал статистики временно удален.
#
# async def _update_defense_stats(user_id: int): ...

async def _update_defense_stats(user_id: int):
    """
    Обновляет статистику защиты для пользователя.
    Updates defense statistics for a user.
    """
    us, _ = await UserSetting.get_or_create(user_id=user_id)
    if us.stats_enabled:
        us.cards_played += 1
        us.cards_beaten += 1
        await us.save()

async def do_defence_card(game: Game, player: Player, atk_card: Card, def_card: Card, gm: GameManager):
    """
    Обрабатывает ход защищающейся картой.
    
    Handles a defending card move.
    """
    try:
        player.play_defence(game, atk_card, def_card)
    except NotAllowedMove as e:
        logger.warning(f"Игрок {player.id} попытался сделать некорректный ход: {e}")
        return
        
    bot = Bot.get_current()
    await _update_defense_stats(player.id)

    # Удаляем сообщения и стикеры, связанные с побитой картой
    announce_id = game.attack_announce_message_ids.pop(atk_card, None)
    if announce_id:
        asyncio.create_task(_delete_message_after_delay(game.id, announce_id, 7))
    sticker_id = game.attack_sticker_message_ids.pop(atk_card, None)
    if sticker_id:
        asyncio.create_task(_delete_message_after_delay(game.id, sticker_id, 7))

    await gm.save_game(game)

    active_players_count = len([p for p in game.players if not p.finished_game])
    # Авто-пас, если атакующий не может больше подкидывать и в игре мало людей
    should_autopass = (not game.attacker_can_continue) and (active_players_count < 3)

    # Если все карты побиты и был пас (или авто-пас), завершаем ход
    if game.all_beaten_cards and (game.is_pass or should_autopass):
        await do_turn(game, gm)
    else:
        toss_more_markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text='↪️ Подкинуть еще', switch_inline_query_current_chat='')]
        ])
        await bot.send_message(
            game.id,
            f"🛡️ <b>{player.mention}</b> побил(а) карту {str(atk_card)} картой {str(def_card)}",
            reply_markup=toss_more_markup,
        )
        
        # Уведомляем, если больше нельзя подкидывать
        if not game.allow_atack and active_players_count > 2:
            await send_no_more_attacks_notification(game)
