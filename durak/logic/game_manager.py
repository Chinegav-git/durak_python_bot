import asyncio
from ..objects import *
from ..db import UserSetting, ChatSetting
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

    @db_session
    def new_game(self, chat: types.Chat, creator: types.User) -> Game:
        """
        Створює нову гру, забезпечуючи стійкість до перезапусків.
        errors:
        - GameAlreadyInChatError (якщо гра вже є в пам'яті)
        """
        # 1. Перевірка наявності гри в пам'яті
        if self.games.get(chat.id):
            raise GameAlreadyInChatError

        # 2. Отримання або створення налаштувань чату та перевірка "завислої" гри
        chat_setting = ChatSetting.get_or_create(chat.id)
        if chat_setting.is_game_active:
            # Якщо гра позначена як активна в БД, але її немає в пам'яті,
            # це означає, що бот перезапускався. Скидаємо стан.
            chat_setting.is_game_active = False

        # 3. Створення нової гри та збереження її в пам'яті
        game = Game(chat, creator)
        self.games[chat.id] = game

        # 4. Позначення гри як активної в базі даних
        chat_setting.is_game_active = True

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
        chat_id = target.chat.id if isinstance(target, Game) else target.id

        # Видалення гри з пам'яті
        game = self.games.pop(chat_id, None)

        # Завжди оновлюємо стан в БД
        chat_setting = ChatSetting.get(id=chat_id)
        if chat_setting:
            chat_setting.is_game_active = False

        # Якщо гри не було в пам'яті, кидаємо помилку
        if game is None:
            raise NoGameInChatError
        
        # Оновлення статистики гравців
        for pl in game.players:
            us = UserSetting.get_or_create(pl.user.id)
            if us.stats:
                us.games_played += 1

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
        message = f"За командою адміністратора, гру примусово завершено!\n\n🏆 Переможець:\n- {winner.user.full_name}\n\n"
        if losers:
            message += "Програвші:\n" + '\n'.join([f"- {loser.user.full_name}" for loser in losers])

        await self.bot.send_message(game.chat.id, message)
        await asyncio.to_thread(self.end_game, game)

    def join_in_game(self, game: Game, user: types.User) -> None:
        """
        errors:
        - GameStartedError, LobbyClosedError, LimitPlayersInGameError, 
        - AlreadyJoinedError, AlreadyJoinedInGlobalError
        """
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
        """
        errors:
        - GameStartedError, NotEnoughPlayersError
        """
        if game.started:
            raise GameStartedError
        if len(game.players) <= 1:
            raise NotEnoughPlayersError
        game.start()

    def player_for_user(self, user: types.User) -> Player | None:
        return next((p for g in self.games.values() for p in g.players if p.user.id == user.id), None)

    def check_user_ex_in_all_games(self, user: types.User) -> bool:
        return self.player_for_user(user) is not None
