import logging
from aiogram import executor
from loader import dp, bot  # Импортируем ОДИН И ТОТ ЖЕ объект dp
from durak.filters import IsAdminFilter

logging.basicConfig(level=logging.INFO)

# ШАГ А: Регистрация фильтра (теперь dp из loader знает про 'is_admin')
dp.filters_factory.bind(IsAdminFilter)

# ШАГ Б: Импорт хендлеров ПОСЛЕ регистрации
from durak import handlers

if __name__ == '__main__':
    # Используем dp из loader для запуска
    executor.start_polling(dp, skip_updates=True)
