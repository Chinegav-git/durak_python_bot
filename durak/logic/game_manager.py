import asyncio
import pickle
from ..objects import *
from ..db import UserSetting, ChatSetting
from pony.orm import db_session

from aiogram import types, Bot
from typing import Dict, List, Union
from redis.asyncio import Redis

from ..objects.errors import PlayerNotFoundError


class GameManager:
    def __init__(self, redis: Redis) -> None:
        self.redis: Redis = redis
        self.notify: Dict[int, List[int]] = dict()
        self.bot: Bot = None

    def _game_key(self, chat_id: int) -> str:
        return f"game:{chat_id}"

    async def _serialize_game(self, game: Game) -> bytes:
        return pickle.dumps(game)

    async def _deserialize_game(self, data: bytes) -> Game:
        game: Game = pickle.loads(data)
        return game

    async def save_game(self, game: Game):
        """Saves a game object to Redis."""
        key = self._game_key(game.id)
        serialized_game = await self._serialize_game(game)
        await self.redis.set(key, serialized_game)

    def set_bot(self, bot: Bot):
        self.bot = bot

    # --- DB-related private methods ---

    @db_session
    def _new_game_db_session(self, chat_id: int, user_id: int):
        """Synchronously handles DB operations for new game creation."""
        chat_setting = ChatSetting.get_or_create(chat_id)
        if chat_setting.is_game_active:
            chat_setting.is_game_active = False # Reset in case of zombie game
        chat_setting.is_game_active = True
        self._update_user_playing_status_db_session([user_id], True)

    @db_session
    def _end_game_db_session(self, chat_id: int, players: List[Player]):
        """Synchronously handles DB operations for ending a game."""
        chat_setting = ChatSetting.get(id=chat_id)
        if chat_setting:
            chat_setting.is_game_active = False

        player_ids = [p.id for p in players]
        self._update_user_playing_status_db_session(player_ids, False)

        for pl in players:
            us = UserSetting.get_or_create(pl.id)
            if us.stats:
                us.games_played += 1

    @db_session
    def _check_user_in_game_db_session(self, user_id: int) -> bool:
        """Checks if a user is marked as playing in the database."""
        user_setting = UserSetting.get(id=user_id)
        return user_setting and user_setting.is_playing

    @db_session
    def _update_user_playing_status_db_session(self, user_ids: List[int], is_playing: bool):
        """Updates the is_playing status for a list of users."""
        for user_id in user_ids:
            user_setting = UserSetting.get_or_create(user_id)
            user_setting.is_playing = is_playing

    # --- Game Logic Helpers ---

    async def is_user_in_any_game(self, user_id: int) -> bool:
        """Checks if a user is currently a player in any active game stored in Redis."""
        game_keys = await self.redis.keys("game:*")
        for key in game_keys:
            serialized_game = await self.redis.get(key)
            if serialized_game:
                game = await self._deserialize_game(serialized_game)
                if any(p.id == user_id for p in game.players):
                    return True
        return False

    def get_game_end_message(self, game: Game) -> str:
        """Generates the game over message based on the game's state, matching the old style."""
        
        if not game.durak:
            # Draw case
            return (
                '🤝 <b>Гру закінчено! Нічия!</b>\n\n'
                'Усі гравці закінчили гру одночасно.'
            )

        # Case with a loser (durak)
        winners = [p for p in game.players if p != game.durak]
        loser = game.durak

        message_parts = ["🎮 <b>Гру закінчено!</b>\n"]

        if winners:
            winners_text = "\n".join([f'🏆 {p.mention}' for p in winners])
            message_parts.append("<b>Переможці:</b>")
            message_parts.append(winners_text)
        else:
            message_parts.append("<b>Переможці:</b>")
            message_parts.append("Немає")
        
        if loser:
            if winners:
                message_parts.append("") # Add a newline for separation
            loser_text = f'💔 {loser.mention}'
            message_parts.append("<b>Програв:</b>")
            message_parts.append(loser_text)

        return "\n".join(message_parts)

    # --- Public methods ---

    async def new_game(self, chat: types.Chat, creator: types.User) -> Game:
        game_key = self._game_key(chat.id)
        if await self.redis.exists(game_key):
            raise GameAlreadyInChatError
        if await self.is_user_in_any_game(creator.id):
            raise AlreadyJoinedInGlobalError

        await asyncio.to_thread(self._new_game_db_session, chat.id, creator.id)
        
        game = Game(
            chat_id=chat.id,
            chat_type=chat.type,
            creator_id=creator.id,
            creator_first_name=creator.first_name,
            creator_username=creator.username
        )
        await self.save_game(game)
        return game

    async def get_game_from_chat(self, chat: Union[types.Chat, int]) -> Game:
        chat_id = chat if isinstance(chat, int) else chat.id
        game_key = self._game_key(chat_id)
        serialized_game = await self.redis.get(game_key)
        if serialized_game:
            game = await self._deserialize_game(serialized_game)
            return game
        raise NoGameInChatError

    async def end_game(self, target: Union[types.Chat, Game]) -> None:
        chat_id = target.id if isinstance(target, Game) else target.id
        game_key = self._game_key(chat_id)
        
        game = None
        if isinstance(target, Game):
            game = target
        else:
            try:
                game = await self.get_game_from_chat(target)
            except NoGameInChatError:
                pass 

        was_deleted = await self.redis.delete(game_key)

        if game:
            players = game.players
            await asyncio.to_thread(self._end_game_db_session, chat_id, players)
        elif was_deleted:
             await asyncio.to_thread(self._end_game_db_session, chat_id, [])
        else:
            await asyncio.to_thread(self._end_game_db_session, chat_id, [])
            raise NoGameInChatError

    async def test_win_game(self, game: Game, winner_id: int):
        """
        Завершує гру та оголошує переможця для тесту.
        """
        if not self.bot:
            return

        winner = game.player_for_id(winner_id)
        if not winner:
            raise ValueError("Гравця з таким ID не знайдено в цій грі.")

        game.started = False
        game.winner = winner
        
        losers = [p for p in game.players if p.id != winner_id]

        message_parts = ["За командою адміністратора, гру примусово завершено!\n"]
        message_parts.append("🏆 Переможець:")
        message_parts.append(f'- <a href="tg://user?id={winner.id}">{winner.first_name}</a>')
        
        if losers:
            message_parts.append("")
            message_parts.append("Програвші:")
            message_parts.extend([f'- <a href="tg://user?id={loser.id}">{loser.first_name}</a>' for loser in losers])

        message = "\n".join(message_parts)
        await self.bot.send_message(game.id, message)
        await self.end_game(game)

    async def join_in_game(self, game: Game, user: types.User) -> None:
        if game.started:
            raise GameStartedError
        if not game.open:
            raise LobbyClosedError
        if len(game.players) >= game.MAX_PLAYERS:
            raise LimitPlayersInGameError
        if any(p.id == user.id for p in game.players):
            raise AlreadyJoinedError
        if await self.is_user_in_any_game(user.id):
            raise AlreadyJoinedInGlobalError

        await asyncio.to_thread(self._update_user_playing_status_db_session, [user.id], True)
        
        player = Player(
            game=game, 
            user_id=user.id, 
            first_name=user.first_name, 
            username=user.username
        )
        game.players.append(player)
        
        await self.save_game(game)

    async def start_game(self, game: Game) -> None:
        if game.started:
            raise GameStartedError
        if len(game.players) <= 1:
            raise NotEnoughPlayersError

        unique_player_ids = {p.id for p in game.players}
        if len(unique_player_ids) != len(game.players):
            await self.end_game(game)
            raise Exception("Критична помилка: виявлено дублювання гравців. Гру було скасовано.")

        game.start()
        await self.save_game(game)