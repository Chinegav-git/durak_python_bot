#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания таблиц базы данных.
Database table creation script.
"""

import asyncio
from durak.db.tortoise_config import TORTOISE_ORM
from tortoise import Tortoise


async def create_tables():
    """Создает таблицы в базе данных."""
    await Tortoise.init(config=TORTOISE_ORM)
    
    # Создаем таблицы
    await Tortoise.generate_schemas()
    
    print("Таблицы успешно созданы!")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(create_tables())
