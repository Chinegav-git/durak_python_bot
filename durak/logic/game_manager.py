import asyncio
from ..objects import *
from ..db import UserSetting
from pony.orm import db_session

from aiogram import types, Bot
from typing import Dict, List, Union


class GameManager:
    def __init__(self) -> None:
        self.games: Dict[int, Game] = dict()
        self.notify: Dict[int, List[int]] = list()
        self.bot: Bot = None

    def set_bot(self, bot: Bot):
        self.bot = bot
    
    def new_game(self, chat: types.Chat, creator: types.User) -> Game:
        """
        errors:

        - GameAlreadyInChatError
        """
        if self.games.get(chat.id, None) is not None:
            raise GameAlreadyInChatError
        
        game = Game(chat, creator)
        self.games[chat.id] = game
        return game
    

    def get_game_from_chat(self, chat: types.Chat) -> Game:
        """errors:

        - NoGameInChatError
        """
        game = self.games.get(chat.id, None)

        if game is not None:
            return game
        raise NoGameInChatError
    
    @db_session
    def end_game(self, target: Union[types.Chat, Game]) -> None:
        """errors:

        - NoGameInChatError
        """
        if isinstance(target, types.Chat):
            chat = target
        else:
            chat = target.chat
        
        game = self.games.get(chat.id, None)
        if game is not None:
            players = game.players
            
            for pl in players:
                # stats
                user = pl.user
                us = UserSetting.get(id=user.id)
                if not us:
                    us = UserSetting(id=user.id)

                if us.stats:
                    us.games_played += 1
            
            del self.games[chat.id]
            return
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

        # 1. Correctly stop the game
        game.started = False
        game.winner = winner

        # 2. Build the detailed message
        losers = [p for p in game.players if p.user.id != winner_id]
        
        message = "За командою адміністратора, гру примусово завершено!\n\n"
        message += f"🏆 Переможець:\n- {winner.user.full_name}\n\n"
        
        if losers:
            message += "Програвші:\n"
            for loser in losers:
                message += f"- {loser.user.full_name}\n"

        await self.bot.send_message(game.chat.id, message)

        # 3. Clean up the game session in a separate thread
        await asyncio.to_thread(self.end_game, game)

    def join_in_game(self, game: Game, user: types.User) -> None:
        """
        errors:

        - GameStartedError
        - LobbyClosedError
        - LimitPlayersInGameError
        - AlreadyJoinedError
        """
        if game.started:
            raise GameStartedError
        if not game.open:
            raise LobbyClosedError
        if len(game.players) >= game.MAX_PLAYERS:
            raise LimitPlayersInGameError
        
        for _player in game.players:
            if user == _player.user:
                raise AlreadyJoinedError
        
        if self.check_user_ex_in_all_games(user):
            raise AlreadyJoinedInGlobalError

        player = Player(game, user)
        game.players.append(player)

        return
        

    def start_game(self, game: Game) -> None:
        """
        errors:

        - GameStartedError
        - NotEnoughPlayersError
        """
        if game.started:
            raise GameStartedError
        if len(game.players) <= 1:
            raise NotEnoughPlayersError
        game.start()
        

    def player_for_user(self, user: types.User) -> Player | None:
        for game in self.games.values():
            for player in game.players:
                if player.user == user:
                    return player
        
        return None
    

    def check_user_ex_in_all_games(self, user: types.User) -> bool:
        """
        True - exist
        False - not exist
        """
        for game in self.games.values():
            for player in game.players:
                if player.user.id == user.id:
                    return True
        
        return False