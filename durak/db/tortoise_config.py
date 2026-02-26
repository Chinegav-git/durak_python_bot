# -*- coding: utf-8 -*-
"""
Файл конфигурации для Tortoise ORM.

ИСПРАВЛЕНО: Конфигурация была явно изменена для принудительного использования PostgreSQL.
Ранее система могла откатываться к SQLite, если переменные окружения были недоступны,
что приводило к созданию миграций для неверной СУБД.

Configuration file for Tortoise ORM.

FIXED: The configuration has been explicitly changed to enforce the use of PostgreSQL.
Previously, the system could fall back to SQLite if environment variables were not available,
which led to creating migrations for the wrong СУБД.
"""

import os
from tortoise import Tortoise

# Загружаем переменные окружения для подключения к БД
# Loading environment variables for DB connection
DB_USER = os.environ.get("POSTGRES_USER", "chinegav")
DB_PASS = os.environ.get("POSTGRES_PASSWORD", "90874513067")
DB_HOST = os.environ.get("POSTGRES_HOST", "127.0.0.1")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_NAME = os.environ.get("POSTGRES_DB", "durak_db")

# Формируем URL для подключения к PostgreSQL
# Generating the connection URL for PostgreSQL
DATABASE_URL = f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Словарь с конфигурацией Tortoise ORM
# Dictionary with Tortoise ORM configuration
TORTOISE_ORM = {
    # Определяет подключения к базам данных.
    # Defines database connections.
    "connections": {
        # "default" - это имя подключения, которое будет использоваться по умолчанию.
        # "default" is the name of the connection that will be used by default.
        "default": DATABASE_URL # URL для подключения к PostgreSQL.
                                # The connection URL for PostgreSQL.
    },
    # "apps" определяет, где Tortoise будет искать модели.
    # "apps" defines where Tortoise will look for models.
    "apps": {
        "models": {
            # Список путей к модулям, содержащим модели.
            # List of paths to modules containing models.
            "models": [
                "durak.db.models",  # Путь ко всем моделям приложения.
                                    # Path to all application models.
                "aerich.models"     # Модели, необходимые для инструмента миграций Aerich.
                                    # Models required for the Aerich migration tool.
            ],
            # Указывает, какое соединение использовать для этого приложения.
            # Specifies which connection to use for this app.
            "default_connection": "default",
        },
    },
}

async def init_db():
    """
    Асинхронная функция для инициализации подключения к базе данных.
    Вызывается при старте приложения.
    Asynchronous function to initialize the database connection.
    Called on application startup.
    """
    await Tortoise.init(config=TORTOISE_ORM)

async def close_db_connection():
    """
    Асинхронная функция для закрытия подключения к базе данных.
    Вызывается при остановке приложения.
    Asynchronous function to close the database connection.
    Called on application shutdown.
    """
    await Tortoise.close_connections()


class DatabaseSession:
    """
    Контекстный менеджер для работы с базой данных.
    Database session context manager.
    """
    async def __aenter__(self):
        # Проверяем, инициализирована ли база данных
        # Check if database is initialized
        if not Tortoise._inited:
            await init_db()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Здесь можно добавить логику очистки транзакций
        # Add transaction cleanup logic here
        pass


def get_db_session():
    """
    Возвращает экземпляр контекстного менеджера для работы с базой данных.
    Returns database session context manager instance.
    """
    return DatabaseSession()
