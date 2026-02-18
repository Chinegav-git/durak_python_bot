import asyncio
import pickle
from contextlib import suppress
from ..objects import *
from ..db.models import UserSetting, ChatSetting

from aiogram import types, Bot
from typing import Dict, List, Union, Optional
from redis.asyncio import Redis

from ..objects.errors import *


class GameManager:
    def __init__(self, redis: Redis) -> None:
        self.redis: Redis = redis
        self.bot: Bot = None

    def _game_key(self, chat_id: int) -> str:
        return f"game:{chat_id}"

    def _user_game_key(self, user_id: int) -> str:
        return f"user_game:{user_id}"

    async def _serialize_game(self, game: Game) -> bytes:
        return pickle.dumps(game)

    async def _deserialize_game(self, data: bytes) -> Game:
        return pickle.loads(data)

    async def save_game(self, game: Game):
        key = self._game_key(game.id)
        serialized_game = await self._serialize_game(game)
        await self.redis.set(key, serialized_game)

    def set_bot(self, bot: Bot):
        self.bot = bot

    async def _new_game_db_session(self, chat_id: int, user_id: int):
        chat_setting, _ = await ChatSetting.get_or_create(id=chat_id)
        # Reset if stuck
        if chat_setting.is_game_active: 
            chat_setting.is_game_active = False
        chat_setting.is_game_active = True
        await chat_setting.save()
        await self._update_user_playing_status_db_session([user_id], True)

    async def _end_game_db_session(self, chat_id: int, players: List[Player]):
        chat_setting = await ChatSetting.get_or_none(id=chat_id)
        if chat_setting:
            chat_setting.is_game_active = False
            await chat_setting.save()

        player_ids = [p.id for p in players]
        await self._update_user_playing_status_db_session(player_ids, False)

        for pl in players:
            us, _ = await UserSetting.get_or_create(id=pl.id)
            if us.stats:
                us.games_played += 1
                await us.save()
    
    async def _leave_game_db_session(self, user_id: int):
        await self._update_user_playing_status_db_session([user_id], False)
        us, _ = await UserSetting.get_or_create(id=user_id)
        if us.stats:
            us.games_played += 1
            await us.save()

    async def _update_user_playing_status_db_session(self, user_ids: List[int], is_playing: bool):
        for user_id in user_ids:
            user_setting, _ = await UserSetting.get_or_create(id=user_id)
            user_setting.is_playing = is_playing
            await user_setting.save()

    async def get_user_game_id(self, user_id: int) -> Optional[int]:
        """Checks if a user is in any game and returns the game chat ID if they are."""
        game_id = await self.redis.get(self._user_game_key(user_id))
        return int(game_id) if game_id else None

    def get_game_end_message(self, game: Game) -> str:
        if not game.durak:
            return '🤝 <b>Гру закінчено! Нічия!</b>\n\nУсі гравці закінчили гру одночасно.'

        winners = [p for p in game.players if p != game.durak]
        loser = game.durak
        message_parts = ["🎮 <b>Гру закінчено!</b>\n"]
        if winners:
            message_parts.append("<b>Переможці:</b>")
            message_parts.append("\n".join([f'🏆 {p.mention}' for p in winners]))
        if loser:
            message_parts.append("\n<b>Програв:</b>")
            message_parts.append(f'💔 {loser.mention}')
        return "\n".join(message_parts)

    async def new_game(self, chat: types.Chat, creator: types.User) -> Game:
        if await self.redis.exists(self._game_key(chat.id)):
            raise GameAlreadyInChatError
        if await self.get_user_game_id(creator.id):
            raise AlreadyJoinedInGlobalError

        await self._new_game_db_session(chat.id, creator.id)
        await self.redis.set(self._user_game_key(creator.id), chat.id)
        
        game = Game(
            chat_id=chat.id, chat_type=chat.type, creator_id=creator.id,
            creator_first_name=creator.first_name, creator_username=creator.username
        )
        await self.save_game(game)
        return game

    async def get_game_from_chat(self, chat_or_id: Union[types.Chat, int]) -> Game:
        chat_id = chat_or_id if isinstance(chat_or_id, int) else chat_or_id.id
        serialized_game = await self.redis.get(self._game_key(chat_id))
        if serialized_game:
            try:
                return await self._deserialize_game(serialized_game)
            except (pickle.UnpicklingError, AttributeError, EOFError) as e:
                await self.redis.delete(self._game_key(chat_id))
                raise NoGameInChatError(f"Corrupted game data: {e}")
        raise NoGameInChatError

    async def end_game(self, target: Union[types.Chat, Game]) -> None:
        chat_id = target.id if isinstance(target, Game) else target.id
        game_key = self._game_key(chat_id)
        
        game = None
        if isinstance(target, Game):
            game = target
        else:
            with suppress(NoGameInChatError):
                game = await self.get_game_from_chat(chat_id)
        
        was_deleted = await self.redis.delete(game_key)

        if game:
            player_ids = [p.id for p in game.players]
            if player_ids:
                user_keys = [self._user_game_key(pid) for pid in player_ids]
                await self.redis.delete(*user_keys)
            
            await self._end_game_db_session(chat_id, game.players)

        elif was_deleted:
            await self._end_game_db_session(chat_id, [])
        else:
            with suppress(Exception):
                 await self._end_game_db_session(chat_id, [])
            raise NoGameInChatError

    async def leave_game(self, game: Game, player: Player):
        """Removes a player from a game and cleans up their state."""
        if player not in game.players:
            return

        game.players.remove(player)

        await self._leave_game_db_session(player.id)
        
        await self.redis.delete(self._user_game_key(player.id))

        if not game.started:
            await self.save_game(game)
            return

        player.leave(game)
        player.finished_game = True

        if len([p for p in game.players if not p.finished_game]) < 2:
            raise NotEnoughPlayersError("Not enough players to continue")
        
        await self.save_game(game)

    async def test_win_game(self, game: Game, winner_id: int):
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
        if await self.get_user_game_id(user.id):
            raise AlreadyJoinedInGlobalError

        await self._update_user_playing_status_db_session([user.id], True)
        await self.redis.set(self._user_game_key(user.id), game.id)

        player = Player(user_id=user.id, first_name=user.first_name, username=user.username)
        game.players.append(player)
        await self.save_game(game)

    async def start_game(self, game: Game) -> None:
        if game.started:
            raise GameStartedError
        if len(game.players) <= 1:
            raise NotEnoughPlayersError

        game.start()
        await self.save_game(game)
