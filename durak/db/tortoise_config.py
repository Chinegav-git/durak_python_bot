# -*- coding: utf-8 -*-
"""
Файл конфигурации для Tortoise ORM.
Определяет параметры подключения к базе данных и указывает расположение моделей.
Configuration file for Tortoise ORM.
Defines database connection parameters and specifies the location of models.
"""

from tortoise import Tortoise
from config import Config

# Словарь с конфигурацией Tortoise ORM
# Dictionary with Tortoise ORM configuration
TORTOISE_ORM = {
    # Определяет подключения к базам данных.
    # Defines database connections.
    "connections": {
        # "default" - это имя подключения, которое будет использоваться по умолчанию.
        # "default" is the name of the connection that will be used by default.
        "default": Config.DATABASE_URL # URL для подключения берется из объекта Config.
                                        # The connection URL is taken from the Config object.
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
