from tortoise import Tortoise
from config import Config

TORTOISE_ORM_CONFIG = {
    "connections": {
        "default": Config.DATABASE_URL
    },
    "apps": {
        "models": {
            "models": [
                "durak.db.user_settings",
                # "durak.db.chat_settings", # Модель временно отключена
                "aerich.models"
            ],
            "default_connection": "default",
        },
    },
}

async def init_db():
    """
    Initializes the Tortoise ORM connection.
    """
    await Tortoise.init(config=TORTOISE_ORM_CONFIG)
    # if Config.DATABASE_URL.startswith("sqlite"):
    #     await Tortoise.generate_schemas() # Отключено, т.к. используется Aerich для миграций

async def close_db_connection():
    """
    Closes the Tortoise ORM connection.
    """
    await Tortoise.close_connections()
