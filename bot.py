import logging
import asyncio

from aiogram import executor

from loader import dp
from durak.filters import IsAdminFilter
from durak.db.tortoise_config import init_db, close_db_connection

# 1. Налаштування логування
logging.basicConfig(level=logging.INFO)

# 2. Реєстрація кастомних фільтрів
# Цей рядок ПОВИНЕН виконуватися ДО імпорту обробників
dp.filters_factory.bind(IsAdminFilter)

# 3. Імпорт обробників
# Тепер, коли фільтри зареєстровані, можна безпечно імпортувати обробники
from durak import handlers

async def on_startup(dispatcher):
    logging.info("Бот запускається...")
    logging.info("Ініціалізація бази даних...")
    await init_db()
    logging.info("Базу даних ініціалізовано.")

async def on_shutdown(dispatcher):
    logging.warning("Бот зупиняється...")
    await close_db_connection()
    logging.info("З'єднання з базою даних закрито.")

if __name__ == '__main__':
    executor.start_polling(
        dp,
        skip_updates=True, 
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )
