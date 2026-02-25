#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для пересоздания таблиц базы данных с правильными типами полей.
Database table recreation script with correct field types.
"""

import asyncio
import sys
import os

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from durak.db.tortoise_config import TORTOISE_ORM
from tortoise import Tortoise
from tortoise.exceptions import OperationalError


async def recreate_tables():
    """
    Пересоздает таблицы с правильными типами полей.
    Recreates tables with correct field types.
    """
    try:
        print("🔄 Подключение к базе данных...")
        await Tortoise.init(config=TORTOISE_ORM)
        
        print("🗑️ Удаление старых таблиц...")
        # Получаем подключение к базе данных
        conn = Tortoise.get_connection("default")
        
        # Удаляем таблицы в правильном порядке (сначала зависимые)
        drop_queries = [
            "DROP TABLE IF EXISTS game_players CASCADE;",
            "DROP TABLE IF EXISTS games CASCADE;",
            "DROP TABLE IF EXISTS chatsettings CASCADE;",
            "DROP TABLE IF EXISTS usersettings CASCADE;",
            "DROP TABLE IF EXISTS chats CASCADE;",
            "DROP TABLE IF EXISTS users CASCADE;",
        ]
        
        for query in drop_queries:
            try:
                await conn.execute(query)
                print(f"✅ Выполнено: {query}")
            except Exception as e:
                print(f"⚠️ Пропущено: {query} - {e}")
        
        print("🔄 Создание новых таблиц...")
        await Tortoise.generate_schemas()
        
        print("✅ Таблицы успешно пересозданы!")
        print("\n📋 Созданные таблицы с BigIntField:")
        print("- users (пользователи) - ID теперь BigInt")
        print("- chats (чаты) - ID теперь BigInt") 
        print("- games (игры) - ID теперь BigInt")
        print("- usersettings (настройки пользователей)")
        print("- chatsettings (настройки чатов)")
        
    except Exception as e:
        print(f"❌ Ошибка при пересоздании таблиц: {e}")
        return False
        
    finally:
        await Tortoise.close_connections()
    
    return True


if __name__ == "__main__":
    print("🚀 Начинаю пересоздание таблиц базы данных...")
    print("=" * 50)
    
    success = asyncio.run(recreate_tables())
    
    if success:
        print("\n🎉 Таблицы успешно пересозданы с BigIntField!")
        print("Теперь можно запускать бота: python bot.py")
    else:
        print("\n💥 Пересоздание таблиц не удалось!")
        print("Проверьте ошибки выше и попробуйте снова.")
