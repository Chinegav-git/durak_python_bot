import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from config import Config
from durak.db.tortoise_config import init_db, close_db_connection
from durak.handlers import router as main_router
from durak.utils.set_bot_commands import set_default_commands

async def on_startup(bot: Bot):
    await set_default_commands(bot)
    await init_db()
    logging.info("Bot started")

async def on_shutdown():
    await close_db_connection()
    logging.info("Bot stopped")

async def main():
    # Явная проверка на наличие токена перед запуском
    if not Config.BOT_TOKEN:
        logging.critical("КРИТИЧЕСКАЯ ОШИБКА: Переменная окружения BOT_TOKEN не найдена.")
        logging.critical("Пожалуйста, укажите токен вашего бота в .env файле и перезапустите приложение.")
        sys.exit(1) # Завершение работы с кодом ошибки

    bot = Bot(token=Config.BOT_TOKEN, parse_mode="Markdown")
    storage = RedisStorage.from_url(f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}")
    dp = Dispatcher(storage=storage)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(main_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
