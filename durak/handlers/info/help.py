# -*- coding: utf-8 -*-
"""
Модуль для обработки информационных команд, таких как /help.
Предоставляет пользователям справочную информацию о том, как использовать бота.

Module for handling informational commands like /help.
Provides users with help information on how to use the bot.
"""

from aiogram import Router, types
from aiogram.filters import Command
from textwrap import dedent

# ИМПОРТ: Команды импортируются из единого источника для консистентности.
from config import Commands

router = Router()

@router.message(Command(Commands.HELP, Commands.START_BOT))
async def help_handler(message: types.Message):
    """
    Обрабатывает команды /help и /start.
    Отправляет пользователю подробное справочное сообщение.
    
    ИСПРАВЛЕНО:
    - Текст полностью переведен на русский язык.
    - Добавлена документация для модуля и обработчика.
    - Жестко закодированная команда /settings заменена на импорт из конфига.

    Handles the /help and /start commands.
    Sends a detailed help message to the user.

    FIXED:
    - The text has been fully translated into Russian.
    - Documentation has been added for the module and the handler.
    - The hardcoded /settings command has been replaced with an import from the config.
    """
    # ИСПРАВЛЕНО: Текст переведен на русский и обновлен.
    help_text = dedent(f"""<b>👋 Привет! Я бот для игры в «Дурака».</b>

<b>Как играть?</b>
1️⃣ Добавьте меня в групповой чат.
2️⃣ Создайте новую игру командой /{Commands.NEW}.
3️⃣ Другие игроки могут присоединиться с помощью команды /{Commands.JOIN}.
4️⃣ Когда все будут готовы (минимум 2 игрока), создатель игры может начать её командой /{Commands.START}.

<b>⚙️ Настройки игры</b>
Используйте команду /{Commands.SETTINGS}, чтобы открыть интерактивное меню, где вы можете:
• **Изменить режим игры:** (текст, стикеры или смешанный).
• **Выбрать тему карт:** Настройте внешний вид карт в чате.

<b>Основные игровые команды:</b>
• /{Commands.NEW} - Создать новую игру.
• /{Commands.JOIN} - Присоединиться к игре.
• /{Commands.START} - Начать игру.
• /{Commands.SETTINGS} - Открыть меню настроек.
• /{Commands.LEAVE} - Покинуть лобби (до начала игры).
• /{Commands.KICK} - Выгнать игрока (для создателя игры).
• /{Commands.KILL} - Принудительно завершить игру (для администраторов чата).
""")
    await message.answer(help_text)
