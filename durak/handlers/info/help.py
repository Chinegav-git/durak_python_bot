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
from durak.utils.i18n import t

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
    help_text = dedent(f"""<b>{t('help.title')}</b>

{t('help.description')}

{t('help.how_to_start')}
{t('help.step1')}
{t('help.step2')}
{t('help.step3')}

<b>⚙️ Налаштування гри</b>
Використовуйте команду /{Commands.SETTINGS}, щоб відкрити інтерактивне меню, де ви можете:
• **Змінити режим гри:** (текст, стікери або змішаний).
• **Вибрати тему карт:** Налаштуйте зовнішній вигляд карт у чаті.

{t('help.commands_list')}
• /{Commands.NEW} - {t('commands.new')}.
• /{Commands.JOIN} - {t('commands.join')}.
• /{Commands.START} - {t('commands.start')}.
• /{Commands.SETTINGS} - {t('commands.settings')}.
• /{Commands.LEAVE} - {t('commands.leave')}.
• /{Commands.KICK} - {t('commands.kick')}.
• /{Commands.KILL} - {t('commands.kill')}.
""")
    await message.answer(help_text)
