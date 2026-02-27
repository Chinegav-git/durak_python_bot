# -*- coding: utf-8 -*-
"""
Скрипт для программного управления Aerich, обходя его CLI.
ИСПРАВЛЕНО: Добавлена отладочная информация для анализа объекта Tortoise.apps
Script to programmatically control Aerich, bypassing its CLI.
FIXED: Added debug information to analyze the Tortoise.apps object.
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

    name = "Initial"
    print(f"1. Имя миграции: '{name}'")

    try:
        print("2. Инициализация Tortoise ORM...")
        await Tortoise.init(
            config=TORTOISE_ORM
        )
        print("   ...Успешно.")

        print("\n--- ОТЛАДКА ---")
        print(f"   Тип Tortoise.apps: {type(Tortoise.apps)}")
        print(f"   Атрибуты Tortoise.apps: {dir(Tortoise.apps)}")
        print("--- КОНЕЦ ОТЛАДКИ ---\n")

        # Эта строка теперь тоже часть отладки. Если она вызовет ошибку,
        # мы будем знать, что у объекта нет даже метода .keys()
        # This line is now also part of debugging. If it errors out,
        # we'll know the object doesn't even have a .keys() method.
        print(f"   Найденные приложения Tortoise (по ключам): {list(Tortoise.apps.keys())}")

        print("\n3. Создание объекта команды Aerich...")
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
