#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания таблиц с правильными типами BigInt через SQL.
Script to create tables with correct BigInt types via SQL.
"""

import asyncio
import sys
import os

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from durak.db.tortoise_config import TORTOISE_ORM
from tortoise import Tortoise


async def create_bigint_tables():
    """
    Создает таблицы с правильными BigInt полями через SQL.
    Creates tables with correct BigInt fields via SQL.
    """
    try:
        print("🔄 Подключение к базе данных...")
        await Tortoise.init(config=TORTOISE_ORM)
        
        print("🗑️ Удаление старых таблиц...")
        conn = Tortoise.get_connection("default")
        
        # Удаляем таблицы
        drop_commands = [
            "DROP TABLE IF EXISTS game_user CASCADE;",
            "DROP TABLE IF EXISTS game CASCADE;", 
            "DROP TABLE IF EXISTS chatsetting CASCADE;",
            "DROP TABLE IF EXISTS usersetting CASCADE;",
            "DROP TABLE IF EXISTS chat CASCADE;",
            "DROP TABLE IF EXISTS user CASCADE;"
        ]
        
        for cmd in drop_commands:
            try:
                await conn.execute_query(cmd)
                print(f"✅ Выполнено: {cmd}")
            except Exception as e:
                print(f"⚠️ Пропущено: {cmd} - {e}")
        
        print("🔄 Создание таблиц с BigInt...")
        
        # Создаем таблицы вручную с правильными типами
        create_commands = [
            # Таблица users
            """
            CREATE TABLE users (
                id BIGINT PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255),
                username VARCHAR(255)
            );
            """,
            
            # Таблица chats  
            """
            CREATE TABLE chats (
                id BIGINT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                type VARCHAR(255) NOT NULL
            );
            """,
            
            # Таблица games
            """
            CREATE TABLE games (
                id BIGINT PRIMARY KEY,
                chat_id BIGINT NOT NULL REFERENCES chats(id),
                status VARCHAR(255) NOT NULL
            );
            """,
            
            # Таблица game_user (связующая)
            """
            CREATE TABLE game_user (
                game_id BIGINT NOT NULL REFERENCES games(id),
                user_id BIGINT NOT NULL REFERENCES users(id),
                PRIMARY KEY (game_id, user_id)
            );
            """,
            
            # Таблица usersettings
            """
            CREATE TABLE usersettings (
                user_id BIGINT PRIMARY KEY REFERENCES users(id),
                stats_enabled BOOLEAN DEFAULT TRUE,
                games_played INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                cards_played INTEGER DEFAULT 0,
                cards_beaten INTEGER DEFAULT 0,
                cards_attack INTEGER DEFAULT 0
            );
            """,
            
            # Таблица chatsettings
            """
            CREATE TABLE chatsettings (
                chat_id BIGINT PRIMARY KEY REFERENCES chats(id),
                game_mode VARCHAR(255) DEFAULT 'p',
                card_theme VARCHAR(255) DEFAULT 'classic',
                sticker_id_helper BOOLEAN DEFAULT FALSE,
                is_game_active BOOLEAN DEFAULT FALSE
            );
            """
        ]
        
        table_names = ["users", "chats", "games", "game_user", "usersettings", "chatsettings"]
        
        for i, cmd in enumerate(create_commands):
            try:
                # Убираем лишние пробелы и переносы
                clean_cmd = " ".join(cmd.split())
                await conn.execute_query(clean_cmd)
                print(f"✅ Создана таблица: {table_names[i]}")
            except Exception as e:
                print(f"❌ Ошибка при создании таблицы {table_names[i]}: {e}")
        
        # Проверяем структуру
        print("\n🔍 Проверка структуры таблицы 'chats':")
        result = await conn.execute_query(
            "SELECT column_name, data_type, numeric_precision FROM information_schema.columns WHERE table_name = 'chats' ORDER BY ordinal_position;"
        )
        for row in result[1]:
            print(f"  - {row[0]}: {row[1]} (precision: {row[2]})")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    print("🔨 Создание таблиц с BigInt через SQL...")
    print("=" * 50)
    
    asyncio.run(create_bigint_tables())
