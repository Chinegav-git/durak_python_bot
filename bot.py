import logging
from aiogram import executor
from loader import dp, bot
from durak.filters import IsAdminFilter

logging.basicConfig(level=logging.INFO)

# Спочатку реєструємо всі кастомні фільтри
dp.filters_factory.bind(IsAdminFilter)

# А вже потім імпортуємо обробники, які їх використовують
from durak.handlers import game, info, gamemode_router

# Реєстрація роутерів
dp.include(game.router)
dp.include(info.router)
dp.include(gamemode_router)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
