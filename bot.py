import logging
from aiogram import executor
from loader import dp, bot  # Імпортуємо ОДИН І ТОЙ ЖЕ об'єкт dp
from durak.filters import IsAdminFilter

# Імпортуємо самі роутери з пакету handlers
from durak.handlers import game, info, gamemode_router

logging.basicConfig(level=logging.INFO)

# Реєстрація фільтра
dp.filters_factory.bind(IsAdminFilter)

# Реєстрація роутерів
dp.include(game.router) # Реєструємо ігровий роутер
dp.include(info.router) # Реєструємо інформаційний роутер
dp.include(gamemode_router) # Реєструємо роутер для /gamemode

if __name__ == '__main__':
    # Використовуємо dp з loader для запуску
    executor.start_polling(dp, skip_updates=True)
