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
from durak.utils import callback_manager
# ИСПРАВЛЕНО: Импортируем GameManager для создания единого экземпляра.
# FIXED: Import GameManager to create a single instance.
from durak.logic.game_manager import GameManager
# from durak.utils.set_bot_commands import set_default_commands


async def on_startup(bot: Bot):
    """
    Выполняется при запуске бота. Устанавливает команды и инициализирует БД.
    Executes when the bot starts. Sets commands and initializes the DB.
    """
    # await set_default_commands(bot)
    await init_db()
    
    # Запускаємо періодичне очищення callback'ів
    # Start periodic callback cleanup
    asyncio.create_task(periodic_callback_cleanup())
    
    logging.info("Bot started")


async def periodic_callback_cleanup():
    """
    Періодичне очищення старих callback'ів.
    Periodic cleanup of old callbacks.
    """
    while True:
        try:
            callback_manager.cleanup_old_callbacks()
            await asyncio.sleep(60)  # Очищення кожну хвилину
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
        logging.critical("Пожалуйста, укажите токен вашего бота в .env файле и перезапустите приложение.")
        sys.exit(1)

    bot = Bot(token=Config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
    storage = RedisStorage.from_url(f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}")

    # Создаем єдиний екземпляр GameManager
    # Create a single instance of GameManager
    redis_client = storage.redis
    gm = GameManager(bot, redis_client)

    # ІСПРАВЛЕНО: Внедряем gm в диспетчер для доступу у всіх обробниках.
    # FIXED: Inject gm into the dispatcher for access in all handlers.
    dp = Dispatcher(storage=storage, game_manager=gm)
    
    # Реєструємо middleware для передачі gm в обробники
    # Register middleware to pass gm to handlers
    dp.update.middleware(GameManagerMiddleware(gm))
    dp.callback_query.middleware(GameManagerMiddleware(gm))

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(setup_handlers(gm))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
