# -*- coding: utf-8 -*-
"""
Основной файл для запуска Telegram-бота.
Отвечает за инициализацию, настройку и запуск всех компонентов бота.
Main file for launching the Telegram bot.
Responsible for initializing, configuring, and starting all bot components.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from config import Config
from durak.db.tortoise_config import init_db, close_db_connection
from durak.handlers import setup as setup_handlers
from durak.middleware import GameManagerMiddleware
from durak.middleware.language_middleware import LanguageMiddleware
from durak.utils import callback_manager
from durak.logic.game_manager import GameManager


async def on_startup(bot: Bot):
    """
    Выполняется при запуске бота. Устанавливает команды и инициализирует БД.
    Executes when the bot starts. Sets commands and initializes the DB.
    """
    await init_db()
    asyncio.create_task(periodic_callback_cleanup())
    logging.info("Bot started")


async def periodic_callback_cleanup():
    """
    Периодическое очищение старых callback'ов.
    Periodic cleanup of old callbacks.
    """
    while True:
        try:
            callback_manager.cleanup_old_callbacks()
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Callback cleanup error: {e}")
            await asyncio.sleep(60)


async def on_shutdown():
    """
    Выполняется при остановке бота. Закрывает соединение с БД.
    Executes when the bot stops. Closes the DB connection.
    """
    await close_db_connection()
    logging.info("Bot stopped")


async def main():
    """
    Основная асинхронная функция для настройки и запуска бота.
    Main asynchronous function for configuring and launching the bot.
    """
    if not Config.BOT_TOKEN:
        logging.critical("КРИТИЧЕСКАЯ ОШИБКА: Переменная окружения BOT_TOKEN не найдена.")
        sys.exit(1)

    bot = Bot(token=Config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    storage = RedisStorage.from_url(f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}")

    redis_client = storage.redis
    gm = GameManager(bot, redis_client)

    dp = Dispatcher(storage=storage, game_manager=gm)
    
    # ИСПРАВЛЕНО: Добавлена регистрация middleware для inline_query.
    # Это устраняет критическую ошибку, из-за которой инлайн-режим
    # (включая кнопку "Мои карты") не работал, так как обработчики
    # не получали необходимые зависимости (gm, l, m).
    # FIXED: Added middleware registration for inline_query.
    # This resolves a critical error where inline mode (including the "My Cards" button)
    # was non-functional because handlers were not receiving required
    # dependencies (gm, l, m).
    dp.update.middleware(GameManagerMiddleware(gm))
    dp.callback_query.middleware(GameManagerMiddleware(gm))
    dp.inline_query.middleware(GameManagerMiddleware(gm))
    
    dp.update.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())
    dp.inline_query.middleware(LanguageMiddleware())

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(setup_handlers(gm))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
