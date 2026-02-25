#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки структуры таблиц базы данных.
Database table structure check script.
"""

import asyncio
import sys
import os

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from durak.db.tortoise_config import TORTOISE_ORM
from tortoise import Tortoise


async def check_tables():
    """
    Проверяет структуру таблиц в базе данных.
    Checks table structure in the database.
    """
    try:
        print("🔄 Подключение к базе данных...")
        await Tortoise.init(config=TORTOISE_ORM)
        
        print("🔍 Проверка структуры таблиц...")
        conn = Tortoise.get_connection("default")
        
        # Проверяем структуру таблицы chat
        print("\n📋 Структура таблицы 'chat':")
        try:
            result = await conn.execute_query(
                "SELECT column_name, data_type, numeric_precision FROM information_schema.columns WHERE table_name = 'chat' ORDER BY ordinal_position;"
            )
            if result[1]:
                for row in result[1]:
                    print(f"  - {row[0]}: {row[1]} (precision: {row[2]})")
            else:
                print("  ❌ Таблица 'chat' не найдена")
        except Exception as e:
            print(f"❌ Ошибка при проверке таблицы chat: {e}")
        
        # Проверяем структуру таблицы user
        print("\n📋 Структура таблицы 'user':")
        try:
            result = await conn.execute_query(
                "SELECT column_name, data_type, numeric_precision FROM information_schema.columns WHERE table_name = 'user' ORDER BY ordinal_position;"
            )
            if result[1]:
                for row in result[1]:
                    print(f"  - {row[0]}: {row[1]} (precision: {row[2]})")
            else:
                print("  ❌ Таблица 'user' не найдена")
        except Exception as e:
            print(f"❌ Ошибка при проверке таблицы user: {e}")
        
        # Проверяем все таблицы
        print("\n📋 Все таблицы в базе данных:")
        try:
            result = await conn.execute_query(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
            )
            if result[1]:
                for row in result[1]:
                    print(f"  - {row[0]}")
            else:
                print("  ❌ Таблицы не найдены")
        except Exception as e:
            print(f"❌ Ошибка при получении списка таблиц: {e}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    print("🔍 Проверка структуры таблиц базы данных...")
    print("=" * 50)
    
    asyncio.run(check_tables())
