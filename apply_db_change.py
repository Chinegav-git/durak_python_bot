# -*- coding: utf-8 -*-
"""
Временный скрипт для прямого применения изменений схемы через Tortoise ORM.
Использует Tortoise.generate_schemas() для добавления недостающих колонок.
Temporary script to directly apply schema changes via Tortoise ORM.
Uses Tortoise.generate_schemas() to add missing columns.
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

async def apply_changes():
    """
    Инициализирует Tortoise ORM и применяет изменения схемы.
    Initializes Tortoise ORM and applies schema changes.
    """
    print("--- Запуск скрипта прямого изменения БД ---")
    try:
        print("1. Инициализация Tortoise ORM...")
        await Tortoise.init(config=TORTOISE_ORM)
        print("   ...Успешно.")

        print("2. Соединение с базой данных...")
        # generate_schemas требует явного получения соединения
        # generate_schemas requires an explicit connection acquisition
        conn = Tortoise.get_connection("default")
        print(f"   ...Успешно. Соединение: {conn.get_dialect()}")

        print("3. Применение изменений схемы (generate_schemas)...")
        # safe=True означает, что существующие таблицы не будут удалены
        # safe=True means existing tables will not be dropped
        await Tortoise.generate_schemas(safe=True)
        print("   ...Схема успешно обновлена.")

        print("\n--- Изменение БД успешно завершено! ---")
        print("Колонка 'auto_pass_enabled' должна быть добавлена в таблицу 'usersettings'.")

    except Exception as e:
        print(f"\nОШИБКА: Не удалось применить изменения - {e}")
    finally:
        await Tortoise.close_connections()
        print("\nСоединения с БД закрыты.")

if __name__ == "__main__":
    run_async(apply_changes())
