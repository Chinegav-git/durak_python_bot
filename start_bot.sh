#!/bin/bash
# RU: Скрипт для запуска Telegram-бота "Дурак" с PostgreSQL и Redis
# EN: Script to run the "Durak" Telegram bot with PostgreSQL and Redis

# RU: Определение цветов для форматированного вывода в консоль.
# EN: Definition of colors for formatted console output.
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# RU: Вывод стартового сообщения.
# EN: Printing the start message.
echo -e "${YELLOW}Запуск бота "Дурак"...${NC}"

# RU: Проверка статуса Redis. Если сервис не активен, скрипт попытается его запустить.
# EN: Checking Redis status. If the service is not active, the script will try to start it.
echo "Проверка статуса Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis работает${NC}"
else
    echo -e "${RED}✗ Redis не запущен. Запускаем...${NC}"
    if ! redis-server --daemonize yes; then
        echo -e "${RED}Ошибка запуска Redis${NC}"
        exit 1
    else
        echo -e "${GREEN}✓ Redis успешно запущен${NC}"
    fi
fi

# RU: Проверка статуса PostgreSQL. Если сервис не активен, скрипт попытается его запустить.
# EN: Checking PostgreSQL status. If the service is not active, the script will try to start it.
echo "Проверка статуса PostgreSQL..."
if sudo -u postgres sh -c "cd /tmp && /usr/local/pgsql/bin/pg_ctl -D /var/lib/postgresql/data status" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL работает${NC}"
else
    echo -e "${RED}✗ PostgreSQL не запущена. Запускаем...${NC}"
    if ! sudo -u postgres sh -c "cd /tmp && /usr/local/pgsql/bin/pg_ctl -D /var/lib/postgresql/data -l /tmp/postgres.log start"; then
        echo -e "${RED}Ошибка запуска PostgreSQL${NC}"
        exit 1
    else
        echo -e "${GREEN}✓ PostgreSQL успешно запущена${NC}"
    fi
fi

# RU: Активация виртуального окружения Python и установка зависимостей.
# EN: Activation of the Python virtual environment and installation of dependencies.
echo "Запуск бота..."
if [ ! -d "venv" ]; then
    # RU: Создание виртуального окружения, если оно не существует.
    # EN: Creating a virtual environment if it does not exist.
    echo -e "${YELLOW}Создание виртуального окружения...${NC}"
    python3 -m venv venv
fi

# RU: Активация виртуального окружения.
# EN: Activating the virtual environment.
source venv/bin/activate

# RU: Проверка и установка зависимостей из файла requirements.txt, если они не установлены.
# EN: Checking and installing dependencies from requirements.txt if they are not already installed.
echo "Проверка зависимостей..."
if ! pip list | grep -q aiogram; then
    echo -e "${YELLOW}Установка зависимостей...${NC}"
    pip install -r requirements.txt
fi

# RU: Инициализация базы данных с использованием Tortoise ORM.
# RU: Этот блок кода запускает асинхронную функцию для создания таблиц в БД.
# EN: Initializing the database using Tortoise ORM.
# EN: This block of code runs an asynchronous function to create tables in the database.
echo "Инициализация базы данных..."
python -c "
import asyncio
from durak.db.tortoise_config import init_db, TORTOISE_ORM
from tortoise import Tortoise

async def init():
    try:
        # RU: Инициализация Tortoise ORM с конфигурацией.
        # EN: Initializing Tortoise ORM with the configuration.
        await Tortoise.init(config=TORTOISE_ORM)
        # RU: Генерация схем таблиц в базе данных.
        # EN: Generating table schemas in the database.
        await Tortoise.generate_schemas()
        print('База данных готова')
    except Exception as e:
        print(f'Ошибка инициализации БД: {e}')
    finally:
        # RU: Закрытие соединений с базой данных.
        # EN: Closing database connections.
        await Tortoise.close_connections()

asyncio.run(init())
"

echo -e "${GREEN}✓ База данных готова${NC}"

# RU: Запуск основного файла бота.
# EN: Running the main bot file.
echo -e "${GREEN}Запуск Telegram-бота...${NC}"
python bot.py
