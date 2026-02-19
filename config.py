from dataclasses import dataclass
from enum import StrEnum
from environs import Env
from typing import List, Tuple, Dict, ClassVar


env = Env()
env.read_env()

# Присваиваем None по умолчанию, чтобы избежать падения при импорте.
# Явная проверка на наличие переменных будет в bot.py.
BOT_TOKEN = env.str("BOT_TOKEN", None)
ADMINS_RAW = env.list("ADMINS", [])

# Обработка списка админов с защитой от неверных данных
ADMINS = []
if ADMINS_RAW:
    try:
        ADMINS = list(map(int, ADMINS_RAW))
    except (ValueError, TypeError):
        # В будущем здесь можно будет добавить логирование
        print(f"ПРЕДУПРЕЖДЕНИЕ: Переменная окружения ADMINS ('{ADMINS_RAW}') содержит нечисловые значения и будет проигнорирована.")

REDIS_HOST = env.str("REDIS_HOST", "localhost")
REDIS_PORT = env.int("REDIS_PORT", 6379)
REDIS_DB = env.int("REDIS_DB", 0)
DATABASE_URL = env.str("DATABASE_URL", "sqlite://durak.sqlite")


@dataclass
class Config:
    BOT_TOKEN: str = BOT_TOKEN
    ADMINS: ClassVar[List[int]] = ADMINS
    DATABASE_URL: str = DATABASE_URL

    WAITING_TIME: int = 120
    MAX_PLAYERS: int = 6
    COUNT_CARDS_IN_START: int = 6
    DEFAULT_GAMEMODE: str = "p"
    DEBUG: bool = False

    # Redis
    REDIS_HOST: str = REDIS_HOST
    REDIS_PORT: int = REDIS_PORT
    REDIS_DB: int = REDIS_DB
    

class Commands:
    NEW: str = 'new'
    JOIN: str = 'join'
    START: str = 'run'
    LEAVE: str = 'leave'
    GLEAVE: str = 'gleave'
    KICK: str = 'kick'
    KILL: str = 'kill'
    HELP: str = 'help'
    START_BOT: str = 'start'
    STATS: str = 'stats'
    OFF_STATS: str = 'off_stats'
    ON_STATS: str = 'on_stats'
    TEST_WIN: str = 'test_win'
    

COMMANDS: List[Tuple[str, str]] = [
    (Commands.NEW, 'Создать новую игру'),
    (Commands.JOIN, 'Присоединиться к игре'),
    (Commands.START, 'Запустить игру'),
    (Commands.LEAVE, 'Покинуть игру или лобби'),
    (Commands.GLEAVE, 'Покинуть игру во всех чатах'),
    (Commands.KICK, 'Выгнать игрока'),
    (Commands.KILL, 'Завершить игру'),
    (Commands.HELP, 'Помощь по боту'),
    (Commands.STATS, 'Ваша статистика'),
    (Commands.OFF_STATS, 'Выключить статистику'),
    (Commands.ON_STATS, 'Включить статистику')
]