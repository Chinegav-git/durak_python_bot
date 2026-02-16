import logging
import time
import asyncio

from aiogram import executor
from aiogram.utils.exceptions import NetworkError

from loader import dp, bot
from durak.filters import IsAdminFilter

logging.basicConfig(level=logging.INFO)

# Реєструємо кастомний фільтр
dp.filters_factory.bind(IsAdminFilter)

# Імпортуємо обробники
# Важливо, щоб ці модулі були імпортовані, 
# оскільки в них знаходяться декоратори @dp.message_handler і т.д.
from durak.handlers import game, info, game_mode, card_theme


if __name__ == '__main__':
    logging.info("Starting bot...")
    while True:
        try:
            # Пропускаємо старі оновлення, щоб уникнути їх обробки після збою
            executor.start_polling(dp, skip_updates=True)
        except (NetworkError, asyncio.TimeoutError) as e:
            logging.warning(f"Network error detected: {e}. Waiting 15 seconds before retry...")
            time.sleep(15)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}. Restarting in 30 seconds...")
            time.sleep(30)
