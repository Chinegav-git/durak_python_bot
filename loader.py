from aiogram import Bot, Dispatcher, types
from config import Config
from durak.logic.game_manager import GameManager
from durak.db.database import db

# 1. Создаем бота
bot = Bot(token=Config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

# 2. Создаем диспетчер
dp = Dispatcher(bot)

# 3. GameManager
gm = GameManager()

# Database init
db.bind('sqlite', 'durak.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

# Button
CHOISE = [[types.InlineKeyboardButton(text='Выбери карту!', switch_inline_query_current_chat='')]]
