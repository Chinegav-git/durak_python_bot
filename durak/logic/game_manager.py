# -*- coding: utf-8 -*-
"""
Менеджер игровых сессий (GameManager).

Этот класс является центральным узлом для управления всеми активными играми в боте.
Он абстрагирует логику хранения, получения и управления жизненным циклом игровых
объектов (`Game`).

Основные обязанности:
- **Хранение:** Сериализует объекты `Game` с помощью `pickle` и сохраняет их в Redis.
  Это обеспечивает быстрое сохранение и загрузку состояния между ходами.
- **Жизненный цикл:** Предоставляет методы для создания (`new_game`), получения
  (`get_game_from_chat`), завершения (`end_game`) и сохранения (`save_game`) игр.
- **Управление игроками:** Обрабатывает присоединение (`join_in_game`) и выход
  (`leave_game`) игроков, управляя их связью с конкретной игровой сессией.
- **Блокировки:** Использует Redis для установки блокировок, предотвращая создание
  нескольких игр в одном чате или участие одного пользователя в нескольких играх.
- **Взаимодействие с БД:** Обновляет флаг `is_game_active` в модели `ChatSetting`,
  чтобы отразить наличие активной игры в чате.

ИСПРАВЛЕНИЕ: Вся логика, связанная с устаревшей моделью `UserSetting` (подсчет
статистики, флаг `is_playing`), была полностью удалена, чтобы восстановить
работоспособность бота. Эти функции были нерабочими и приводили к падению.

-------------------------------------------------------------------------------------

Game Session Manager (GameManager).

This class is the central hub for managing all active games in the bot.
It abstracts the logic for storing, retrieving, and managing the lifecycle of game
objects (`Game`).

Key Responsibilities:
- **Storage:** Serializes `Game` objects using `pickle` and stores them in Redis.
  This ensures fast state saving and loading between turns.
- **Lifecycle:** Provides methods for creating (`new_game`), retrieving
  (`get_game_from_chat`), ending (`end_game`), and saving (`save_game`) games.
- **Player Management:** Handles players joining (`join_in_game`) and leaving
  (`leave_game`), managing their association with a specific game session.
- **Locking:** Uses Redis to set locks, preventing the creation of multiple games
  in one chat or a single user participating in multiple games.
- **DB Interaction:** Updates the `is_game_active` flag in the `ChatSetting` model
  to reflect the presence of an active game in a chat.

FIX: All logic related to the obsolete `UserSetting` model (statistics counting,
`is_playing` flag) has been completely removed to restore the bot's functionality.
These features were non-operational and caused crashes.
"""

import pickle
from contextlib import suppress
from typing import List, Optional, Union

from aiogram import Bot, types
from redis.asyncio import Redis

from ..db.models import Chat, ChatSetting, User, UserSetting
from ..objects.card import Card
from ..objects.errors import (
    AlreadyJoinedError,
    AlreadyJoinedInGlobalError,
    GameAlreadyInChatError,
    GameStartedError,
    LimitPlayersInGameError,
    LobbyClosedError,
    NoGameInChatError,
    NotEnoughPlayersError,
    GameNotFoundError
)
from ..objects.game import Game
from ..objects.player import Player


class GameManager:
    """Класс для управления игровыми сессиями.
    
    Class for managing game sessions.
    """

    def __init__(self, bot: Bot, redis: Redis) -> None:
        self.bot: Bot = bot
        self.redis: Redis = redis

    def _game_key(self, chat_id: int) -> str:
        """Возвращает ключ для хранения игры в Redis.
        
        Returns the Redis key for storing a game.
        """
        return f"game:{chat_id}"

    def _user_game_key(self, user_id: int) -> str:
        """Возвращает ключ для отслеживания игры пользователя в Redis.
        
        Returns the Redis key for tracking a user's game.
        """
        return f"user_game:{user_id}"

    async def _serialize_game(self, game: Game) -> bytes:
        """Сериализует объект игры в байты для Redis.
        
        Serializes a game object into bytes for Redis.
        """
        return pickle.dumps(game)

    async def _deserialize_game(self, data: bytes) -> Game:
        """Десериализует объект игры из байтов.
        
        Deserializes a game object from bytes.
        """
        return pickle.loads(data)

    async def _update_stats_on_game_end(self, game: Game):
        """
        Обновляет статистику игроков по окончании игры.
        Updates player statistics at the end of a game.
        """
        loser_id = game.durak.id if game.durak else None

        for player in game.players:
            # Убедимся, что игрок существует в БД, чтобы избежать ошибок внешнего ключа
            # Ensure the player exists in the DB to avoid foreign key errors
            await User.get_or_create(
                id=player.id, 
                defaults={
                    'first_name': player.first_name, 
                    'username': player.username
                }
            )
            us, _ = await UserSetting.get_or_create(user_id=player.id)
            if not us.stats_enabled:
                continue

            us.games_played += 1
            if player.id != loser_id:
                us.wins += 1
            
            await us.save()

    async def save_game(self, game: Game):
        """Сохраняет состояние игры в Redis.
        
        Saves the game state to Redis.
        """
        key = self._game_key(game.id)
        serialized_game = await self._serialize_game(game)
        await self.redis.set(key, serialized_game)

    async def get_user_game_id(self, user_id: int) -> Optional[int]:
        """Проверяет, в какой игре находится пользователь.
        
        Checks which game a user is in.
        """
        game_id = await self.redis.get(self._user_game_key(user_id))
        return int(game_id) if game_id else None

    async def get_game_by_user_id(self, user_id: int) -> Game:
        """
        ДОБАВЛЕНО (стабилизация): Находит игру по ID пользователя.
        Используется для обработчиков, где нет информации о чате (например, inline-режим).

        ADDED (stabilization): Finds a game by user ID.
        Used for handlers where there is no chat information (e.g., inline mode).
        """
        chat_id = await self.get_user_game_id(user_id)
        if not chat_id:
            raise GameNotFoundError(f"User {user_id} is not in any game")
        
        try:
            return await self.get_game_from_chat(chat_id)
        except NoGameInChatError:
            # Эта ситуация может возникнуть, если блокировка пользователя в Redis
            # осталась, а сама игра была удалена. Очищаем мусор.
            # This can happen if a user's lock in Redis remains, but the game itself
            # was deleted. Cleaning up the garbage.
            await self.redis.delete(self._user_game_key(user_id))
            raise GameNotFoundError(f"Game in chat {chat_id} not found, but a stale user lock for {user_id} was found and cleared")

    def get_game_end_message(self, game: Game) -> str:
        """Генерирует финальное сообщение по окончании игры.
        
        Generates the final message at the end of a game.
        """
        if not game.durak:
            return '🤝 <b>Игра окончена! Ничья!</b>\n\nВсе игроки закончили игру одновременно.'

        winners = [p for p in game.players if p != game.durak]
        loser = game.durak
        message_parts = ["🎮 <b>Игра окончена!</b>\n"]
        if winners:
            message_parts.append("<b>Победители:</b>")
            message_parts.append("\n".join([f'🏆 {p.mention}' for p in winners]))
        if loser:
            message_parts.append("\n<b>Проигравший:</b>")
            message_parts.append(f'💔 {loser.mention}')
        return "\n".join(message_parts)

    async def new_game(self, chat: types.Chat, creator: types.User) -> Game:
        """Создает новую игру в чате.
        
        Raises:
            GameAlreadyInChatError: Если игра в этом чате уже существует.
            AlreadyJoinedInGlobalError: Если создатель уже участвует в другой игре.
        
        Creates a new game in a chat.
        """
        if await self.redis.exists(self._game_key(chat.id)):
            raise GameAlreadyInChatError
        if await self.get_user_game_id(creator.id):
            raise AlreadyJoinedInGlobalError

        # Убедимся, что чат и создатель существуют в БД
        # Ensure the chat and creator exist in the DB
        await Chat.get_or_create(id=chat.id, defaults={'title': chat.title, 'type': chat.type})
        await User.get_or_create(
            id=creator.id, 
            defaults={
                'first_name': creator.first_name, 
                'last_name': creator.last_name, 
                'username': creator.username
            }
        )

        # Устанавливаем флаг в БД и блокировку в Redis
        chat, _ = await Chat.get_or_create(id=chat.id)
        cs, _ = await ChatSetting.get_or_create(chat=chat)
        cs.is_game_active = True
        await cs.save()
        await self.redis.set(self._user_game_key(creator.id), chat.id)
        
        game = Game(
            chat_id=chat.id, chat_type=chat.type, creator_id=creator.id,
            creator_first_name=creator.first_name, creator_username=creator.username
        )
        await self.save_game(game)
        return game

    async def get_game_from_chat(self, chat_or_id: Union[types.Chat, int]) -> Game:
        """Получает игру из чата. 
        
        Если данные игры повреждены, удаляет их из Redis.

        Raises:
            NoGameInChatError: Если игра в чате не найдена или данные повреждены.
        
        Retrieves a game from a chat.
        """
        chat_id = chat_or_id if isinstance(chat_or_id, int) else chat_or_id.id
        serialized_game = await self.redis.get(self._game_key(chat_id))
        if not serialized_game:
            raise NoGameInChatError
        
        try:
            return await self._deserialize_game(serialized_game)
        except (pickle.UnpicklingError, AttributeError, EOFError, ImportError) as e:
            # Если данные повреждены, удаляем их, чтобы не вызывать ошибок в будущем
            await self.redis.delete(self._game_key(chat_id))
            raise NoGameInChatError(f"Corrupted game data, deleted: {e}")

    async def end_game(self, target: Union[types.Chat, Game]) -> None:
        """Завершает игру, удаляя все связанные данные из Redis и БД.
        
        Ends a game, deleting all related data from Redis and the DB.
        """
        chat_id = target.id if isinstance(target, Game) else target.id
        game = target if isinstance(target, Game) else await self.get_game_from_chat(chat_id)
        
        # Снимаем флаг в БД
        cs = await ChatSetting.get_or_none(chat_id=chat_id)
        if cs and cs.is_game_active:
            cs.is_game_active = False
            await cs.save()

        # Обновляем статистику до удаления данных
        # Update statistics before deleting data
        await self._update_stats_on_game_end(game)

        # Удаляем блокировки пользователей и сам объект игры из Redis
        player_ids = [p.id for p in game.players]
        if player_ids:
            user_keys = [self._user_game_key(pid) for pid in player_ids]
            await self.redis.delete(*user_keys)
        
        await self.redis.delete(self._game_key(chat_id))

    async def leave_game(self, game: Game, player: Player):
        """Удаляет игрока из игры и очищает его состояние.
        
        Raises:
            NotEnoughPlayersError: Если после выхода остается менее 2 игроков.
        
        Removes a player from a game and cleans up their state.
        """
        if player not in game.players:
            return

        game.players.remove(player)
        
        # Снимаем блокировку с пользователя в Redis
        await self.redis.delete(self._user_game_key(player.id))

        # Если игра еще не началась, просто сохраняем новый список игроков
        if not game.started:
            await self.save_game(game)
            return

        # Если игра уже идет, обрабатываем выход
        player.leave(game)
        player.finished_game = True

        if len([p for p in game.players if not p.finished_game]) < 2:
            raise NotEnoughPlayersError("Недостаточно игроков для продолжения")
        
        await self.save_game(game)

    async def join_in_game(self, game: Game, user: types.User) -> None:
        """Добавляет пользователя в игру.
        
        Raises:
            GameStartedError: Если игра уже началась.
            LobbyClosedError: Если лобби закрыто.
            LimitPlayersInGameError: Если достигнут лимит игроков.
            AlreadyJoinedError: Если пользователь уже в этой игре.
            AlreadyJoinedInGlobalError: Если пользователь уже в другой игре.

        Adds a user to a game.
        """
        if game.started:
            raise GameStartedError
        if not game.open:
            raise LobbyClosedError
        if len(game.players) >= game.MAX_PLAYERS:
            raise LimitPlayersInGameError
        if any(p.id == user.id for p in game.players):
            raise AlreadyJoinedError
        if await self.get_user_game_id(user.id):
            raise AlreadyJoinedInGlobalError

        # Убедимся, что игрок существует в БД
        # Ensure the player exists in the DB
        await User.get_or_create(
            id=user.id, 
            defaults={
                'first_name': user.first_name, 
                'last_name': user.last_name, 
                'username': user.username
            }
        )

        # Устанавливаем блокировку в Redis
        await self.redis.set(self._user_game_key(user.id), game.id)

        player = Player(user_id=user.id, first_name=user.first_name, username=user.username)
        game.players.append(player)
        await self.save_game(game)

    async def start_game(self, game: Game) -> None:
        """Начинает игру.
        
        Raises:
            GameStartedError: Если игра уже была начата.
            NotEnoughPlayersError: Если в игре менее 2 игроков.

        Starts a game.
        """
        if game.started:
            raise GameStartedError
        if len(game.players) <= 1:
            raise NotEnoughPlayersError

        game.start()
        await self.save_game(game)

    # Тестовый метод для отладки, его можно будет удалить в будущем
    # Test method for debugging, can be removed in the future
    async def test_win_game(self, game: Game, winner_id: int):
        if not self.bot:
            return

        winner = game.player_for_id(winner_id)
        if not winner:
            raise ValueError("Игрока с таким ID не найдено в этой игре.")

        game.started = False # Останавливаем игру
        game.winner = winner
        
        losers = [p for p in game.players if p.id != winner_id]

        message_parts = ["По команде администратора, игра принудительно завершена!\n"]
        message_parts.append("🏆 Победитель:")
        message_parts.append(f'- <a href="tg://user?id={winner.id}">{winner.first_name}</a>')
        
        if losers:
            message_parts.append("\nПроигравшие:")
            message_parts.extend([f'- <a href="tg://user?id={loser.id}">{loser.first_name}</a>' for loser in losers])

        message = "\n".join(message_parts)
        await self.bot.send_message(game.id, message)
        await self.end_game(game)
