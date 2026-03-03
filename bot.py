# -*- coding: utf-8 -*-
# RU: Основной файл для запуска Telegram-бота. Отвечает за инициализацию, настройку и запуск всех компонентов.
# EN: Main file for launching the Telegram bot. Responsible for initializing, configuring, and starting all components.

# RU: Системные импорты для логирования, асинхронности и работы с системой.
# EN: System imports for logging, asynchronous operations, and system interaction.
import asyncio
import logging
import sys

# RU: Импорты основной библиотеки aiogram для создания бота, диспетчера и хранилища.
# EN: Imports from the main aiogram library for creating the bot, dispatcher, and storage.
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

# RU: Импорты конфигурации и внутренних модулей проекта.
# EN: Imports of configuration and internal project modules.
from config import Config
from durak.db.tortoise_config import init_db, close_db_connection
from durak.handlers import setup as setup_handlers
from durak.middleware import GameManagerMiddleware
from durak.middleware.language_middleware import LanguageMiddleware
from durak.utils import callback_manager
from durak.logic.game_manager import GameManager


async def on_startup(bot: Bot):
    # RU: Функция, выполняемая при запуске бота. Инициализирует базу данных и запускает фоновую задачу очистки колбэков.
    # EN: Function executed when the bot starts. Initializes the database and starts a background task for callback cleanup.
    await init_db()
    asyncio.create_task(periodic_callback_cleanup())
    logging.info("Bot started")


async def periodic_callback_cleanup():
    # RU: Бесконечный цикл, который периодически (каждые 60 секунд) удаляет устаревшие колбэки для предотвращения утечек памяти.
    # EN: An infinite loop that periodically (every 60 seconds) removes outdated callbacks to prevent memory leaks.
    while True:
        try:
            callback_manager.cleanup_old_callbacks()
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Callback cleanup error: {e}")
            await asyncio.sleep(60)


async def on_shutdown():
    # RU: Функция, выполняемая при остановке бота. Корректно закрывает соединение с базой данных.
    # EN: Function executed when the bot stops. Correctly closes the database connection.
    await close_db_connection()
    logging.info("Bot stopped")


async def main():
    # RU: Основная асинхронная функция. Собирает и запускает все компоненты бота.
    # EN: The main asynchronous function. Assembles and starts all bot components.
    
    # RU: Критическая проверка наличия токена. Если токен отсутствует, бот не сможет запуститься.
    # EN: Critical check for the token. If the token is missing, the bot cannot start.
    if not Config.BOT_TOKEN:
        logging.critical("КРИТИЧЕСКАЯ ОШИБКА: Переменная окружения BOT_TOKEN не найдена.")
        sys.exit(1)

    # RU: Инициализация объекта бота с указанием токена и режима парсинга по умолчанию.
    # EN: Initializing the Bot object with the token and default parse mode specified.
    bot = Bot(token=Config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    
    # RU: Инициализация хранилища Redis для управления состояниями (FSM) и другими данными.
    # EN: Initializing Redis storage for managing states (FSM) and other data.
    storage = RedisStorage.from_url(f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}")

    # RU: Создание экземпляра менеджера игр, который управляет всей игровой логикой.
    # EN: Creating an instance of the game manager, which controls all game logic.
    redis_client = storage.redis
    gm = GameManager(bot, redis_client)

    # RU: Инициализация диспетчера с передачей ему хранилища и менеджера игр.
    # EN: Initializing the dispatcher and passing the storage and game manager to it.
    dp = Dispatcher(storage=storage, game_manager=gm)
    
    # RU: Регистрация middleware для всех типов обновлений. Они добавляют в обработчики нужные зависимости (gm, l, m).
    # EN: Registering middleware for all update types. They add necessary dependencies (gm, l, m) to the handlers.
    # ИСПРАВЛЕНО: Добавлена регистрация middleware для inline_query.
    # FIXED: Added middleware registration for inline_query.
    dp.update.middleware(GameManagerMiddleware(gm))
    dp.callback_query.middleware(GameManagerMiddleware(gm))
    dp.inline_query.middleware(GameManagerMiddleware(gm))
    
    dp.update.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())
    dp.inline_query.middleware(LanguageMiddleware())

    # RU: Регистрация функций, которые будут выполнены при старте и остановке бота.
    # EN: Registering functions to be executed on bot startup and shutdown.
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # RU: Подключение всех роутеров (обработчиков команд и сообщений) из пакета durak.handlers.
    # EN: Including all routers (command and message handlers) from the durak.handlers package.
    dp.include_router(setup_handlers(gm))

    # RU: Удаление вебхука и запуск бота в режиме опроса (polling).
    # EN: Deleting the webhook and starting the bot in polling mode.
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    # RU: Точка входа в программу. Настраивает базовое логирование и запускает основную асинхронную функцию.
    # EN: The entry point of the program. Sets up basic logging and runs the main asynchronous function.
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
