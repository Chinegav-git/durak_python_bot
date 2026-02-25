#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для принудительного пересоздания таблиц базы данных.
Force database table recreation script.
"""

import asyncio
import sys
import os

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from durak.db.tortoise_config import TORTOISE_ORM
from tortoise import Tortoise


async def force_recreate():
    """
    Принудительно пересоздает таблицы.
    Force recreates tables.
    """
    try:
        print("🔄 Подключение к базе данных...")
        await Tortoise.init(config=TORTOISE_ORM)
        
        print("🗑️ Принудительное удаление всех таблиц...")
        conn = Tortoise.get_connection("default")
        
        # Выполняем SQL для удаления таблиц по одной
        drop_commands = [
            "DROP TABLE IF EXISTS game_players CASCADE;",
            "DROP TABLE IF EXISTS games CASCADE;",
            "DROP TABLE IF EXISTS chatsettings CASCADE;",
            "DROP TABLE IF EXISTS usersettings CASCADE;",
            "DROP TABLE IF EXISTS chats CASCADE;",
            "DROP TABLE IF EXISTS users CASCADE;"
        ]
        
        for cmd in drop_commands:
            try:
                await conn.execute_query(cmd)
                print(f"✅ Выполнено: {cmd}")
            except Exception as e:
                print(f"⚠️ Пропущено: {cmd} - {e}")
        
        print("🔄 Создание новых таблиц с BigIntField...")
        await Tortoise.generate_schemas()
        print("✅ Таблицы созданы")
        
        # Проверяем структуру
        print("\n🔍 Проверка новой структуры:")
        result = await conn.execute_query(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'chats' ORDER BY ordinal_position;"
        )
        for row in result[1]:
            print(f"  - {row[0]}: {row[1]}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    print("🔨 Принудительное пересоздание таблиц...")
    print("=" * 50)
    
    asyncio.run(force_recreate())
