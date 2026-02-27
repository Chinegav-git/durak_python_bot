# -*- coding: utf-8 -*-
"""
Скрипт для программного управления Aerich, обходя его CLI.
ИСПРАВЛЕНО: Конструктор Command() вызывается с правильным именованным
аргументом 'tortoise_config'.
Script to programmatically control Aerich, bypassing its CLI.
FIXED: The Command() constructor is called with the correct keyword
argument 'tortoise_config'.
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

    # Имя для "нулевой" миграции, фиксирующей текущее состояние
    # Name for the "zero" migration to capture the current state
    name = "Initial"

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
        # ИСПРАВЛЕНО: Используем правильный аргумент tortoise_config
        # FIXED: Using the correct tortoise_config argument
        command = Command(tortoise_config=TORTOISE_ORM)
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
