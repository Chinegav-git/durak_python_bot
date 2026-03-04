# -*- coding: utf-8 -*-
"""
Модуль для отображения статистики игрока и обработки устаревших команд.

Module for displaying player statistics and handling legacy commands.
"""

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.markdown import hbold, hcode

# ИМПОРТ: Команды импортируются из единого источника для консистентности.
# IMPORT: Commands are imported from a single source for consistency.
from config import Commands

# ИМПОРТ: Модели для доступа к данным
# IMPORT: Models for data access
from durak.db.models import UserSetting

# ИМПОРТ: Система локализации
# IMPORT: Localization system
from durak.utils.i18n import I18n

router = Router()


@router.message(Command(Commands.STATS))
async def show_stats_handler(message: types.Message, l: I18n):
    """
    Обрабатывает команду /stats и отображает статистику пользователя.
    Handles the /stats command and displays the user's statistics.
    """
    user_id = message.from_user.id

    # Ищем настройки пользователя в базе данных, подгружая связанный объект user
    # Look for user settings in the database, preloading the related user object
    user_settings = await UserSetting.get_or_none(user_id=user_id).prefetch_related('user')

    if user_settings and user_settings.stats_enabled:
        # Рассчитываем винрейт, избегая деления на ноль
        # Calculate win rate, avoiding division by zero
        games_played = user_settings.games_played
        wins = user_settings.wins
        win_rate = (wins / games_played * 100) if games_played > 0 else 0

        # Формируем текст сообщения с использованием HTML-разметки и ключей локализации
        # Format the message text using HTML markup and localization keys
        stats_text_localized = [
            hbold(l.t('stats.header', player_name=user_settings.user.first_name)),
            "",
            l.t('stats.games_played', count=hcode(games_played)),
            l.t('stats.wins', count=hcode(wins)),
            l.t('stats.win_rate', percentage=hcode(f'{win_rate:.1f}%')),
            "---",
            l.t('stats.cards_played', count=hcode(user_settings.cards_played)),
            l.t('stats.cards_beaten', count=hcode(user_settings.cards_beaten)),
            l.t('stats.cards_attack', count=hcode(user_settings.cards_attack)),
        ]

        await message.answer('\n'.join(stats_text_localized), parse_mode="HTML")
    else:
        # Сообщаем, что статистика отключена или не найдена
        # Inform that statistics are disabled or not found
        await message.answer(l.t(
            'stats.stats_disabled',
            settings_command=f"/{Commands.SETTINGS}"
        ))


@router.message(Command(Commands.OFF_STATS, Commands.ON_STATS))
async def stats_redirect_handler(message: types.Message, l: I18n):
    """
    Обрабатывает устаревшие команды /on_stats, /off_stats.
    Сообщает пользователю, что эта функция была перенесена в меню /settings.

    Handles the legacy commands /on_stats, /off_stats.
    Informs the user that this functionality has been moved to the /settings menu.
    """
    await message.answer(l.t(
        'settings.stats_control',
        command=f"/{Commands.SETTINGS}"
    ))
