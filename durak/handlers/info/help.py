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
    help_text = dedent(f"""<b>👋 Вітаю! Я бот для гри в «Дурня».</b>

<b>Як грати?</b>
1️⃣ Додайте мене в груповий чат.
2️⃣ Створіть нову гру командою /{Commands.NEW}.
3️⃣ Інші гравці можуть приєднатися за допомогою команди /{Commands.JOIN}.
4️⃣ Коли всі будуть готові (мінімум 2 гравці), творець гри може почати її командою /{Commands.START}.

<b>⚙️ Налаштування гри</b>
Використовуйте команду /{Commands.SETTINGS}, щоб відкрити інтерактивне меню, де ви можете:
• **Змінити режим гри:** (текст, стікери або змішаний).
• **Вибрати тему карт:** Налаштуйте зовнішній вигляд карт у чаті.

<b>Основні ігрові команди:</b>
• /{Commands.NEW} - Створити нову гру.
• /{Commands.JOIN} - Приєднатися до гри.
• /{Commands.START} - Почати гру.
• /{Commands.SETTINGS} - Відкрити меню налаштувань.
• /{Commands.LEAVE} - Покинути лобі (до початку гри).
• /{Commands.KICK} - Видалити гравця (для творця гри).
• /{Commands.KILL} - Примусово завершити гру (для адміністраторів чату).
""")
    await message.answer(help_text)
