from aiogram import Bot, Dispatcher, types
from config import Config, Commands
from durak.logic.game_manager import GameManager
from durak.db.database import db
import os
import redis.asyncio as redis

# 1. Create bot
bot = Bot(token=Config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

# 2. Create dispatcher
dp = Dispatcher(bot)

# 3. Redis connection
redis_pool = redis.from_url(
    f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}"
)

# 4. GameManager
gm = GameManager(redis=redis_pool)
gm.set_bot(bot)  # Pass the bot instance to the GameManager

# Database init
# Define the absolute path to the database file
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'durak.sqlite')
db.bind('sqlite', db_path, create_db=True)
db.generate_mapping(create_tables=True)

# Button
CHOISE = [[types.InlineKeyboardButton(text='Вибери карту!', switch_inline_query_current_chat='')]]
