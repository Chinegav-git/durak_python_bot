from aiogram import Bot, Dispatcher, types
from config import Config, Commands
from durak.logic.game_manager import GameManager
from durak.db.database import db
import os

# 1. Создаем бота
bot = Bot(token=Config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

# 2. Создаем диспетчер
dp = Dispatcher(bot)

# 3. GameManager
gm = GameManager()
gm.set_bot(bot)  # Передаем экземпляр бота в GameManager
#Commands = COMMANDS

# Database init
# Определяем абсолютный путь к файлу базы данных
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'durak.sqlite')
db.bind('sqlite', db_path, create_db=True)
db.generate_mapping(create_tables=True)

# Button
CHOISE = [[types.InlineKeyboardButton(text='Вибери карту!', switch_inline_query_current_chat='')]]
