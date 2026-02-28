# -*- coding: utf-8 -*-
# migrations/scripts/0_5_add_autopass_fields.py
"""
Ручная миграция для добавления полей 'autopass_enabled' и 'auto_pass_enabled'.
Manual migration to add the 'autopass_enabled' and 'auto_pass_enabled' fields.
"""

import asyncio
import sys
import os
from environs import Env
from tortoise import Tortoise, run_async

# Добавляем корневую директорию проекта в sys.path
# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Убедитесь, что переменные окружения загружены
# Ensure environment variables are loaded
Env().read_env()

from durak.db.tortoise_config import TORTOISE_ORM

async def run_migration():
    """
    Выполняет SQL-запрос для изменения схемы.
    Executes the SQL query to alter the schema.
    """
    print("--- Запуск ручной миграции: 0_5_add_autopass_fields ---")
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        conn = Tortoise.get_connection("default")

        print("Применяем SQL-изменения...")
        # ПРЯМОЙ SQL ЗАПРОС
        await conn.execute_script(
            '''
            ALTER TABLE "chatsettings" ADD COLUMN "autopass_enabled" BOOLEAN NOT NULL DEFAULT TRUE;
            ALTER TABLE "usersettings" ADD COLUMN "auto_pass_enabled" BOOLEAN NOT NULL DEFAULT FALSE;
            '''
        )
        print("...Успешно.")

    except Exception as e:
        # Если колонка уже существует, это не ошибка
        # If the column already exists, it's not an error
        if "already exists" in str(e):
            print("...Колонка уже существует, пропущено.")
        else:
            print(f"ОШИБКА: {e}")
    finally:
        await Tortoise.close_connections()
        print("--- Миграция завершена ---")

if __name__ == "__main__":
    run_async(run_migration())
