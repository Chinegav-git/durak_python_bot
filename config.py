# -*- coding: utf-8 -*-
"""
Файл конфигурации.
Загружает переменные окружения и определяет основные настройки бота.
Configuration file.
Loads environment variables and defines the main settings for the bot.
"""

from dataclasses import dataclass
from enum import StrEnum
from environs import Env
from typing import List, Tuple, Dict, ClassVar

# Инициализируем environs для чтения переменных окружения
# Initialize environs to read environment variables
env = Env()
env.read_env()

# --- Загрузка переменных из .env файла ---
# --- Loading variables from the .env file ---
# Токен Telegram бота. Присваиваем None по умолчанию, чтобы избежать падения при импорте.
# Telegram bot token. Assign None by default to avoid crashing on import.
BOT_TOKEN = env.str("BOT_TOKEN", None)

# Список администраторов бота (строковый).
# List of bot administrators (raw string).
ADMINS_RAW = env.list("ADMINS", [])

# Обработка списка админов с защитой от неверных данных
# Processing the admin list with protection against invalid data
ADMINS = []
if ADMINS_RAW:
    try:
        ADMINS = list(map(int, ADMINS_RAW))
    except (ValueError, TypeError):
        # В будущем здесь можно будет добавить логирование
        # Logging can be added here in the future
        print(f"ПРЕДУПРЕЖДЕНИЕ: Переменная окружения ADMINS ('{ADMINS_RAW}') содержит нечисловые значения и будет проигнорирована.")

# Настройки подключения к Redis
# Redis connection settings
REDIS_HOST = env.str("REDIS_HOST", "localhost")
REDIS_PORT = env.int("REDIS_PORT", 6379)
REDIS_DB = env.int("REDIS_DB", 0)

# URL для подключения к базе данных
# Database connection URL
DATABASE_URL = env.str("DATABASE_URL", "sqlite://durak.sqlite")


@dataclass
class Config:
    """
    Основной класс конфигурации, используемый в приложении.
    Содержит как статические, так и загружаемые из .env файла параметры.
    The main configuration class used in the application.
    Contains both static and .env-loaded parameters.
    """
    # --- Загружаемые переменные ---
    # --- Loaded variables ---
    BOT_TOKEN: str = BOT_TOKEN
    ADMINS: ClassVar[List[int]] = ADMINS
    DATABASE_URL: str = DATABASE_URL

    # --- Игровые константы ---
    # --- Game constants ---
    # Время ожидания в лобби (в секундах)
    # Lobby waiting time (in seconds)
    WAITING_TIME: int = 120

    # Максимальное количество игроков в одной игре
    # Maximum number of players in a single game
    MAX_PLAYERS: int = 6

    # Количество карт, раздаваемых в начале игры
    # Number of cards dealt at the start of the game
    COUNT_CARDS_IN_START: int = 6

    # Игровой режим по умолчанию. 'p' - стикеры и кнопки
    # Default game mode. 'p' - stickers and buttons
    DEFAULT_GAMEMODE: str = "p"

    # Режим отладки
    # Debug mode
    DEBUG: bool = False

    # --- Настройки Redis ---
    # --- Redis Settings ---
    REDIS_HOST: str = REDIS_HOST
    REDIS_PORT: int = REDIS_PORT
    REDIS_DB: int = REDIS_DB
    

class Commands:
    """
    Класс, содержащий текстовые представления команд бота для удобного доступа.
    
    A class containing text representations of bot commands for easy access.
    """
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
    

# Список команд и их описаний для меню в Telegram
# List of commands and their descriptions for the Telegram menu
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