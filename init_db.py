# -*- coding: utf-8 -*-
"""
Скрипт для инициализации базы данных с нуля.
Создает все таблицы на основе текущего состояния моделей Tortoise ORM.

Script to initialize the database from scratch.
Creates all tables based on the current state of the Tortoise ORM models.
"""

import asyncio
from environs import Env
from tortoise import Tortoise, run_async

# Загрузка переменных окружения
# Loading environment variables
env = Env()
env.read_env()

# Импорт конфигурации БД
# Importing DB configuration
from durak.db.tortoise_config import TORTOISE_ORM

async def initialize_database():
    """
    Инициализирует Tortoise ORM и создает все таблицы.
    Initializes Tortoise ORM and creates all tables.
    """
    print("--- Запуск скрипта инициализации БД ---")
    try:
        print("1. Инициализация Tortoise ORM...")
        # Подключаемся к БД, но без указания конкретных моделей,
        # так как они уже определены в TORTOISE_ORM
        # Connecting to the DB, but without specifying models,
        # as they are already defined in TORTOISE_ORM
        await Tortoise.init(config=TORTOISE_ORM)
        print("   ...Успешно.")

        print("2. Создание таблиц на основе моделей (generate_schemas)...")
        # safe=False означает, что он попытается создать все таблицы.
        # Использовать только для инициализации пустой БД!
        # safe=False means it will try to create all tables.
        # Use only for initializing an empty DB!
        await Tortoise.generate_schemas(safe=False)
        print("   ...Таблицы успешно созданы.")

        print("\n--- Инициализация БД успешно завершена! ---")
        print("Все таблицы, определенные в моделях, были созданы в базе данных.")

    except Exception as e:
        print(f"\nОШИБКА: Не удалось инициализировать БД - {e}")
    finally:
        await Tortoise.close_connections()
        print("\nСоединения с БД закрыты.")

if __name__ == "__main__":
    # Используем run_async для запуска асинхронной функции
    # Using run_async to run the asynchronous function
    run_async(initialize_database())
