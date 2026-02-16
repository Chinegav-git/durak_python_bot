import asyncio
from ..objects import *
from ..db import UserSetting, ChatSetting
from pony.orm import db_session

from aiogram import types, Bot
from typing import Dict, List, Union

from ..objects.errors import PlayerNotFoundError


class GameManager:
    def __init__(self) -> None:
        self.games: Dict[int, Game] = dict()
        self.notify: Dict[int, List[int]] = dict()
        self.bot: Bot = None

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

        player_ids = [p.user.id for p in players]
        self._update_user_playing_status_db_session(player_ids, False)

        for pl in players:
            us = UserSetting.get_or_create(pl.user.id)
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

    def is_user_in_any_game(self, user_id: int) -> bool:
        """Checks if a user is currently a player in any active, in-memory game."""
        for game in self.games.values():
            for player in game.players:
                if player.user.id == user_id:
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
            winners_text = "\n".join([f'🏆 {p.user.get_mention(as_html=True)}' for p in winners])
            message_parts.append("<b>Переможці:</b>")
            message_parts.append(winners_text)
        else:
            message_parts.append("<b>Переможці:</b>")
            message_parts.append("Немає")
        
        if loser:
            if winners:
                message_parts.append("") # Add a newline for separation
            loser_text = f'💔 {loser.user.get_mention(as_html=True)}'
            message_parts.append("<b>Програв:</b>")
            message_parts.append(loser_text)

        return "\n".join(message_parts)

    # --- Public methods ---

    def new_game(self, chat: types.Chat, creator: types.User) -> Game:
        if self.games.get(chat.id):
            raise GameAlreadyInChatError
        if self.is_user_in_any_game(creator.id):
            raise AlreadyJoinedInGlobalError

        self._new_game_db_session(chat.id, creator.id)
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
            # If no game object, at least mark the chat as not having an active game
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
        message_parts.append(f'- <a href="tg://user?id={winner.user.id}">{winner.user.full_name}</a>')
        
        if losers:
            message_parts.append("")
            message_parts.append("Програвші:")
            message_parts.extend([f'- <a href="tg://user?id={loser.user.id}">{loser.user.full_name}</a>' for loser in losers])

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
        if self.is_user_in_any_game(user.id):
            raise AlreadyJoinedInGlobalError

        self._update_user_playing_status_db_session([user.id], True)
        player = Player(game, user)
        game.players.append(player)

    def start_game(self, game: Game) -> None:
        if game.started:
            raise GameStartedError
        if len(game.players) <= 1:
            raise NotEnoughPlayersError

        # Mitigate the original bug's consequences
        unique_player_ids = {p.user.id for p in game.players}
        if len(unique_player_ids) != len(game.players):
            self.end_game(game)
            raise Exception("Критична помилка: виявлено дублювання гравців. Гру було скасовано.")

        game.start()
