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
gm.set_bot(bot)

# --- ВАЖНЫЙ БЛОК: ИМПОРТ ВСЕХ МОДЕЛЕЙ ПЕРЕД ГЕНЕРАЦИЕЙ МАППИНГА ---
# Импортируем стандартные настройки (UserSetting, ChatSetting)
from durak.db import user_settings, chat_settings
# Импортируем новые модели для игры в мемы
from durak.db.meme_models import MemeSession, MemeEntry, MemeVote
# ----------------------------------------------------------------

# Database init
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'durak.sqlite')

# Привязываем базу данных
if not db.provider:
    db.bind('sqlite', db_path, create_db=True)

# Генерируем таблицы. Теперь Pony видит ВСЕ модели (и Дурака, и Меми)
db.generate_mapping(create_tables=True)

db_session = db

# Button
CHOISE = [[types.InlineKeyboardButton(text='Вибери карту!', switch_inline_query_current_chat='')]]