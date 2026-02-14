import asyncio
from ..objects import *
from ..db import UserSetting, ChatSetting
from pony.orm import db_session

from aiogram import types, Bot
from typing import Dict, List, Union


class GameManager:
    def __init__(self) -> None:
        self.games: Dict[int, Game] = dict()
        self.notify: Dict[int, List[int]] = dict()
        self.bot: Bot = None

    def set_bot(self, bot: Bot):
        self.bot = bot

    # --- DB-related private methods ---

    @db_session
    def _new_game_db_session(self, chat_id: int):
        """Synchronously handles DB operations for new game creation."""
        chat_setting = ChatSetting.get_or_create(chat_id)
        if chat_setting.is_game_active:
            chat_setting.is_game_active = False
        chat_setting.is_game_active = True

    @db_session
    def _end_game_db_session(self, chat_id: int, players: List[Player]):
        """Synchronously handles DB operations for ending a game."""
        chat_setting = ChatSetting.get(id=chat_id)
        if chat_setting:
            chat_setting.is_game_active = False

        for pl in players:
            us = UserSetting.get_or_create(pl.user.id)
            if us.stats:
                us.games_played += 1

    # --- Game Logic Helpers ---

    def get_game_end_message(self, game: Game) -> str:
        """Generates the game over message based on the game's state."""
        winners = [p for p in game.players if p.finished_game and p != game.durak]
        losers = [game.durak] if game.durak else []

        if not winners and not losers:
            return "🎉 Гру завершено!\n\nНічия!"

        message_parts = ["🎉 Гру завершено!\n"]

        if winners:
            title = "🏆 Переможці:" if len(winners) > 1 else "🏆 Переможець:"
            message_parts.append(title)
            message_parts.extend([f"- {p.user.full_name}" for p in winners])
        
        if losers:
            if winners:
                message_parts.append("")
            message_parts.append("Програвші:")
            message_parts.extend([f"- {p.user.full_name}" for p in losers])

        return "\n".join(message_parts)

    # --- Public methods ---

    def new_game(self, chat: types.Chat, creator: types.User) -> Game:
        if self.games.get(chat.id):
            raise GameAlreadyInChatError
        self._new_game_db_session(chat.id)
        game = Game(chat, creator)
        self.games[chat.id] = game
        return game

    def get_game_from_chat(self, chat: types.Chat) -> Game:
        game = self.games.get(chat.id, None)
        if game is not None:
            return game
        raise NoGameInChatError

    def end_game(self, target: Union[types.Chat, Game]) -> None:
        chat_id = target.chat.id if isinstance(target, Game) else target.id
        game = self.games.pop(chat_id, None)
        if game:
            players = game.players
            self._end_game_db_session(chat_id, players)
        else:
            self._end_game_db_session(chat_id, [])
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
        
        losers = [p for p in game.players if p.user.id != winner_id]

        message_parts = ["За командою адміністратора, гру примусово завершено!\n"]
        message_parts.append("🏆 Переможець:")
        message_parts.append(f"- {winner.user.full_name}")
        
        if losers:
            message_parts.append("")
            message_parts.append("Програвші:")
            message_parts.extend([f"- {loser.user.full_name}" for loser in losers])

        message = "\n".join(message_parts)
        await self.bot.send_message(game.chat.id, message)
        await asyncio.to_thread(self.end_game, game)

    def join_in_game(self, game: Game, user: types.User) -> None:
        if game.started:
            raise GameStartedError
        if not game.open:
            raise LobbyClosedError
        if len(game.players) >= game.MAX_PLAYERS:
            raise LimitPlayersInGameError
        if any(p.user.id == user.id for p in game.players):
            raise AlreadyJoinedError
        if self.check_user_ex_in_all_games(user):
            raise AlreadyJoinedInGlobalError
        
        player = Player(game, user)
        game.players.append(player)

    def start_game(self, game: Game) -> None:
        if game.started:
            raise GameStartedError
        if len(game.players) <= 1:
            raise NotEnoughPlayersError
        game.start()

    def player_for_user(self, user: types.User) -> Player | None:
        return next((p for g in self.games.values() for p in g.players if p.user.id == user.id), None)

    def check_user_ex_in_all_games(self, user: types.User) -> bool:
        return self.player_for_user(user) is not None
