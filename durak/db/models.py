# -*- coding: utf-8 -*-
"""
Определение моделей базы данных с использованием Tortoise ORM.
Database model definitions using Tortoise ORM.
"""

from tortoise import fields, models


class User(models.Model):
    """
    Модель, представляющая пользователя Telegram.
    Model representing a Telegram user.
    """
    # Уникальный идентификатор пользователя (Telegram ID)
    # Unique user identifier (Telegram ID)
    id = fields.BigIntField(pk=True)

    # Имя пользователя
    # User's first name
    first_name = fields.CharField(max_length=255)

    # Фамилия пользователя (может отсутствовать)
    # User's last name (optional)
    last_name = fields.CharField(max_length=255, null=True)

    # Username пользователя в Telegram (может отсутствовать)
    # User's Telegram username (optional)
    username = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "users"


class Chat(models.Model):
    """
    Модель, представляющая чат в Telegram.
    Model representing a Telegram chat.
    """
    # Уникальный идентификатор чата (Telegram ID)
    # Unique chat identifier (Telegram ID)
    id = fields.BigIntField(pk=True)

    # Название чата
    # Chat title
    title = fields.CharField(max_length=255)

    # Тип чата (например, 'private', 'group', 'supergroup')
    # Chat type (e.g., 'private', 'group', 'supergroup')
    type = fields.CharField(max_length=255)

    class Meta:
        table = "chats"


class Game(models.Model):
    """
    Модель, представляющая игровую сессию.
    Эта модель не используется для хранения состояния, а лишь для учета в БД.
    Model representing a game session.
    This model is not used for state storage, but only for DB records.
    """
    # Уникальный идентификатор игры
    # Unique game identifier
    id = fields.BigIntField(pk=True)

    # Внешний ключ на чат, в котором проходит игра
    # Foreign key to the chat where the game is being played
    chat = fields.ForeignKeyField("models.Chat", related_name="games")

    # Связь многие-ко-многим с игроками, участвующими в игре
    # Many-to-many relationship with players participating in the game
    players = fields.ManyToManyField("models.User", related_name="games")

    # Текущий статус игры (например, 'lobby', 'playing', 'finished')
    # Current status of the game (e.g., 'lobby', 'playing', 'finished')
    status = fields.CharField(max_length=255)

    class Meta:
        table = "games"

class UserSetting(models.Model):
    """
    Модель для хранения настроек и статистики пользователя.
    Обеспечивает сохранение данных между игровыми сессиями.
    Model for storing user settings and statistics.
    Ensures data persistence between game sessions.
    """
    # Связь один-к-одному с пользователем. ID пользователя является первичным ключом.
    # One-to-one relationship with a user. The user ID is the primary key.
    user = fields.OneToOneField("models.User", related_name="settings", pk=True)

    # Включен ли сбор статистики для этого пользователя
    # Whether statistics collection is enabled for this user
    stats_enabled = fields.BooleanField(default=True)

    # --- Поля статистики ---
    # --- Statistics Fields ---
    games_played = fields.IntField(default=0)
    wins = fields.IntField(default=0)
    cards_played = fields.IntField(default=0)
    cards_beaten = fields.IntField(default=0)
    cards_attack = fields.IntField(default=0)

    class Meta:
        table = "usersettings"


class ChatSetting(models.Model):
    """
    Модель для хранения настроек чата, специфичных для бота.
    Model for storing chat settings specific to the bot.
    """
    # Связь один-к-одному с чатом. ID чата является первичным ключом.
    # One-to-one relationship with a chat. The chat ID is the primary key.
    chat = fields.OneToOneField("models.Chat", related_name="settings", pk=True)

    # Игровой режим, выбранный для чата ('p' - картинки, 't' - текст)
    # Game mode selected for the chat ('p' - pictures, 't' - text)
    game_mode = fields.CharField(max_length=255, default="p")

    # Тема карт, выбранная для чата
    # Card theme selected for the chat
    card_theme = fields.CharField(max_length=255, default="classic")

    # Включен ли помощник по ID стикеров
    # Whether the sticker ID helper is enabled
    sticker_id_helper = fields.BooleanField(default=False)

    # Флаг, указывающий, активна ли игра в данный момент в чате.
    # Flag indicating whether a game is currently active in the chat.
    is_game_active = fields.BooleanField(default=False)

    class Meta:
        table = "chatsettings"
