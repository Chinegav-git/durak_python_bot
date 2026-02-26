#!/bin/bash
# Скрипт для запуска Telegram-бота "Дурак" с PostgreSQL и Redis

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Запуск бота "Дурак"...${NC}"

# Проверка статуса Redis
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

# Проверка статуса PostgreSQL
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

# Активация виртуального окружения и запуск бота
echo "Запуск бота..."
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Создание виртуального окружения...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Проверка зависимостей
echo "Проверка зависимостей..."
if ! pip list | grep -q aiogram; then
    echo -e "${YELLOW}Установка зависимостей...${NC}"
    pip install -r requirements.txt
fi

# Инициализация базы данных при необходимости
echo "Инициализация базы данных..."
python -c "
import asyncio
from durak.db.tortoise_config import init_db, TORTOISE_ORM
from tortoise import Tortoise

async def init():
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        print('База данных готова')
    except Exception as e:
        print(f'Ошибка инициализации БД: {e}')
    finally:
        await Tortoise.close_connections()

asyncio.run(init())
"

echo -e "${GREEN}✓ База данных готова${NC}"

# Запуск бота
echo -e "${GREEN}Запуск Telegram-бота...${NC}"
python bot.py
