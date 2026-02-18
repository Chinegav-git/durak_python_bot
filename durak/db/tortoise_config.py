from tortoise import Tortoise

async def init_db():
    """
    Initializes the Tortoise ORM connection to the SQLite database.
    """
    await Tortoise.init(
        db_url="sqlite://durak.sqlite",
        modules={"models": [
            "durak.db.user_settings",
            "durak.db.chat_settings"
        ]}
    )
    await Tortoise.generate_schemas()

async def close_db_connection():
    """
    Closes the Tortoise ORM connection.
    """
    await Tortoise.close_connections()
