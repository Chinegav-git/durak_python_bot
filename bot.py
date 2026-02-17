import logging
import time
import asyncio

from aiogram import executor
from aiogram.utils.exceptions import NetworkError

from loader import dp, bot
from durak.filters import IsAdminFilter
from durak import handlers

logging.basicConfig(level=logging.INFO)

# Реєструємо кастомний фільтр
dp.filters_factory.bind(IsAdminFilter)


if __name__ == '__main__':
    logging.info("Starting bot...")
    
    # Стандартний запуск без автоматичного перезапуску
    executor.start_polling(dp, skip_updates=True)
