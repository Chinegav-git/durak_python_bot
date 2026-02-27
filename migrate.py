# -*- coding: utf-8 -*-
"""
Скрипт для программного управления Aerich, обходя его CLI.
ИСПРАВЛЕНО: Конструктор Command() вызывается без аргументов, чтобы он
самостоятельно читал конфигурацию из pyproject.toml.
Script to programmatically control Aerich, bypassing its CLI.
FIXED: The Command() constructor is called without arguments to allow it
to read the configuration from pyproject.toml on its own.
"""

import asyncio
import sys
from environs import Env
from tortoise import Tortoise
from aerich import Command

# Критически важно: загружаем .env ПЕРЕД импортом конфига
# CRITICAL: load .env BEFORE importing the config
env = Env()
env.read_env()

# Теперь импортируем конфиг, который использует переменные окружения
# Now import the config that uses the environment variables
from durak.db.tortoise_config import TORTOISE_ORM

async def main():
    """
    Основная функция, которая инициализирует БД и запускает команды aerich.
    Main function that initializes the DB and runs aerich commands.
    """
    print("--- Запуск миграции в программном режиме ---")

    # Получаем имя миграции из аргументов командной строки
    # Get migration name from command line arguments
    args = sys.argv[1:]
    # ИСПРАВЛЕНО: Даем миграции осмысленное имя "Initial"
    # FIXED: Giving the migration a meaningful name "Initial"
    name = "Initial" if not args else " ".join(args)

    print(f"1. Имя миграции: '{name}'")

    try:
        print("2. Инициализация Tortoise ORM...")
        await Tortoise.init(
            config=TORTOISE_ORM
        )
        print("   ...Успешно.")

        if not Tortoise.apps:
            print("   ОШИБКА: Tortoise.apps не был инициализирован!")
            return
        
        print(f"   Найденные приложения Tortoise: {list(Tortoise.apps.keys())}")

        print("3. Создание объекта команды Aerich...")
        # ИСПРАВЛЕНО: Вызываем без аргументов, aerich сам найдет pyproject.toml
        # FIXED: Call without arguments, aerich will find pyproject.toml itself
        command = Command()
        print("   ...Успешно.")

        print(f"4. Генерация миграции '{name}'...")
        await command.migrate(name)
        print("   ...Миграция успешно создана.")
        print("--- Миграция завершена ---")

    except Exception as e:
        print(f"\nОШИБКА: Произошло исключение - {e}")
    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())
