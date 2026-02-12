import logging
from aiogram import Bot, Dispatcher, executor
from config import Config
from durak.filters import IsAdminFilter

# 1. Настройка логов
logging.basicConfig(level=logging.INFO)

# 2. Инициализация
bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher(bot)

# 3. РЕГИСТРАЦИЯ ФИЛЬТРА (Обязательно до импорта хендлеров!)
dp.filters_factory.bind(IsAdminFilter)

# 4. ИМПОРТ ХЕНДЛЕРОВ (После регистрации фильтров)
from durak import handlers

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
