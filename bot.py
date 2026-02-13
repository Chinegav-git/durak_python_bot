import logging
from aiogram import executor
from loader import dp, bot
from durak.filters import IsAdminFilter

logging.basicConfig(level=logging.INFO)

# Реєструємо кастомний фільтр
dp.filters_factory.bind(IsAdminFilter)

# Імпортуємо обробники
# Важливо, щоб ці модулі були імпортовані, 
# оскільки в них знаходяться декоратори @dp.message_handler і т.д.
from durak.handlers import game, info, game_mode


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
