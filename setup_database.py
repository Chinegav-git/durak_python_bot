#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для инициализации и создания таблиц базы данных.
Database initialization and table creation script.

Использование:
python setup_database.py

Этот скрипт:
1. Подключается к базе данных PostgreSQL
2. Создает все необходимые таблицы для бота
3. Инициализирует структуру базы данных

Required:
- PostgreSQL должен быть запущен
- База данных durak_db должна существовать
- Переменные окружения или настройки в .env должны быть корректными
"""

import asyncio
import sys
import os

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from durak.db.tortoise_config import TORTOISE_ORM
from tortoise import Tortoise


async def setup_database():
    """
    Инициализирует подключение к базе данных и создает таблицы.
    Initializes database connection and creates tables.
    """
    try:
        print("🔄 Подключение к базе данных...")
        await Tortoise.init(config=TORTOISE_ORM)
        
        print("🔄 Создание таблиц...")
        await Tortoise.generate_schemas()
        
        print("✅ Таблицы успешно созданы!")
        print("\n📋 Созданные таблицы:")
        print("- users (пользователи)")
        print("- chats (чаты)")
        print("- games (игры)")
        print("- usersettings (настройки пользователей)")
        print("- chatsettings (настройки чатов)")
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        print("\n🔧 Возможные решения:")
        print("1. Убедитесь, что PostgreSQL запущен")
        print("2. Проверьте, что база данных 'durak_db' существует")
        print("3. Проверьте настройки подключения в .env файле")
        print("4. Убедитесь, что пользователь 'chinegav' имеет права на базу данных")
        return False
        
    finally:
        await Tortoise.close_connections()
    
    return True


if __name__ == "__main__":
    print("🚀 Начинаю установку базы данных для Durak Bot...")
    print("=" * 50)
    
    success = asyncio.run(setup_database())
    
    if success:
        print("\n🎉 База данных успешно настроена!")
        print("Теперь можно запускать бота: python bot.py")
    else:
        print("\n💥 Настройка базы данных не удалась!")
        print("Проверьте ошибки выше и попробуйте снова.")
