# -*- coding: utf-8 -*-
"""
Модуль, определяющий главную сущность "Игра".

Этот модуль содержит класс `Game`, который является ядром всей игровой логики.
Он управляет состоянием игры, объединяя в себе колоду, игроков и игровое поле.
Класс отвечает за запуск игры, смену ходов, обработку атак и защит, а также
определение победителя и проигравшего.

--------------------------------------------------------------------------------------

Module defining the main "Game" entity.

This module contains the `Game` class, which is the core of all game logic.
It manages the game state, combining the deck, players, and the game field.
The class is responsible for starting the game, handling turns, processing attacks
and defenses, and determining the winner and the loser.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Optional

from config import Config
# ИСПРАВЛЕНО: Импорты сделаны явными.
from .card import Card, Suits
from .deck import Deck
from .errors import DeckEmptyError
from .player import Player

logger = logging.getLogger(__name__)


class Game:
    """
    Представляет одну игровую сессию в чате.

    Attributes:
        id (int): ID чата, в котором проходит игра.
        chat_type (str): Тип чата (e.g., 'group', 'private').
        deck (Deck): Объект колоды.
        field (Dict[Card, Optional[Card]]): Игровое поле, где ключ - атакующая карта,
            а значение - защищающаяся карта (или None, если карта не побита).
        trump (Optional[Suits]): Козырная масть для текущей игры.
        started (bool): Флаг, указывающий, началась ли игра.
        open (bool): Флаг, открыта ли игра для присоединения новых игроков.
        mode (str): Режим отображения игры в чате (из конфига).
        creator_id (int): ID пользователя, создавшего игру.
        players (List[Player]): Список всех игроков в игре.
        attacker_index (int): Индекс текущего атакующего игрока в списке `players`.
        winner (Optional[Player]): Игрок, который победил (вышел первым).
        durak (Optional[Player]): Игрок, который проиграл.
        is_pass (bool): Флаг, указывающий, сказал ли кто-то из атакующих "пас".
        is_final (bool): Флаг, указывающий, что идет финальный раунд игры.
        attack_announce_message_ids (Dict[Card, int]): Словарь для хранения ID сообщений
            с анонсом атакующих карт.
        attack_sticker_message_ids (Dict[Card, int]): Словарь для хранения ID сообщений
            со стикерами атакующих карт.
        defender_cards_on_round_start (int): Количество карт у защищающегося в начале раунда.
        round_attackers (List[Player]): Список игроков, которые атаковали в текущем раунде.
        COUNT_CARDS_IN_START (int): Начальное количество карт в руке.
        MAX_PLAYERS (int): Максимальное количество игроков.
    """

    def __init__(self, chat_id: int, chat_type: str, creator_id: int, creator_first_name: str, creator_username: Optional[str]) -> None:
        self.id = chat_id
        self.chat_type: str = chat_type
        self.deck: Deck = Deck()
        self.field: Dict[Card, Optional[Card]] = {}
        # ИСПРАВЛЕНО: Аннотация типа для козыря исправлена.
        self.trump: Optional[Suits] = None
        self.started: bool = False
        self.open: bool = True
        self.mode: str = Config.DEFAULT_GAMEMODE

        self.creator_id: int = creator_id
        self.players: List[Player] = [
            Player(creator_id, creator_first_name, creator_username)
        ]

        self.attacker_index: int = 0
        self.winner: Optional[Player] = None
        self.durak: Optional[Player] = None
        self.is_pass: bool = False
        self.is_final: bool = False

        self.attack_announce_message_ids: Dict[Card, int] = {}
        self.attack_sticker_message_ids: Dict[Card, int] = {}
        
        self.defender_cards_on_round_start: int = 0
        self.round_attackers: List[Player] = []

        self.COUNT_CARDS_IN_START: int = Config.COUNT_CARDS_IN_START
        self.MAX_PLAYERS: int = Config.MAX_PLAYERS

    def _update_game_status(self):
        """
        ИСПРАВЛЕНО: Логика, изменяющая состояние, вынесена из @property.
        Проверяет, вышли ли игроки из игры (если у них кончились карты, а в колоде пусто),
        и определяет победителя и проигравшего, если игра подходит к концу.
        
        FIXED: State-mutating logic moved out of the @property.
        Checks if players have left the game (if they ran out of cards while the deck is empty),
        and determines the winner and loser if the game is ending.
        """
        if not self.deck.cards:
            for player in self.players:
                if not player.cards and not player.finished_game:
                    player.finished_game = True

        active_players = [p for p in self.players if not p.finished_game]

        if len(active_players) <= 1:
            if not self.winner and len(self.players) > 1:
                # Победитель - тот, кто уже закончил игру, если он еще не назначен.
                self.winner = next((p for p in self.players if p.finished_game), None)
            
            # Проигравший - последний оставшийся активный игрок.
            self.durak = active_players[0] if active_players else None
            
            # Если активных игроков не осталось (например, ничья), проигравшего нет.
            if not active_players:
                self.durak = None

    @property
    def game_is_over(self) -> bool:
        """
        ИСПРАВЛЕНО: Свойство теперь только проверяет, окончена ли игра, не изменяя её состояние.
        Сначала обновляет статусы, затем проверяет количество активных игроков.
        
        FIXED: The property now only checks if the game is over without changing its state.
        It first updates statuses, then checks the number of active players.
        """
        if not self.started:
            return False
        
        self._update_game_status() 
        active_players = [p for p in self.players if not p.finished_game]
        return len(active_players) <= 1

    def player_for_id(self, user_id: int) -> Optional[Player]:
        """Находит объект игрока по его ID."""
        return next((p for p in self.players if p.id == user_id), None)

    def start(self):
        """
        Запускает игру: создает колоду, определяет козырь и раздает карты.
        
        Starts the game: creates a deck, determines the trump, and deals cards.
        """
        self.deck._fill_cards()
        self.trump = self.deck.trump
        self.started = True
        self.take_cards_from_deck()
        
        opponent = self.opponent_player
        if opponent:
            self.defender_cards_on_round_start = len(opponent.cards)

    def rotate_players(self, lst: List[Player], index: int) -> List[Player]:
        """Вспомогательная функция для ротации списка игроков."""
        return lst[index:] + lst[:index]

    @property
    def attacking_cards(self) -> List[Card]:
        """Возвращает список всех карт, которыми атакуют в текущем раунде."""
        return list(self.field.keys())

    @property
    def defending_cards(self) -> List[Card]:
        """Возвращает список всех карт, которыми защищаются (отбиваются) в текущем раунде."""
        return [card for card in self.field.values() if card is not None]

    @property
    def any_unbeaten_card(self) -> bool:
        """Возвращает True, если на поле есть хотя бы одна не побитая карта."""
        return any(c is None for c in self.field.values())

    @property
    def all_beaten_cards(self) -> bool:
        """Возвращает True, если все атакующие карты на поле были побиты."""
        return all(c is not None for c in self.field.values()) and bool(self.field)

    @property
    def current_player(self) -> Player:
        """Текущий атакующий игрок."""
        return self.players[self.attacker_index]

    @property
    def opponent_player(self) -> Optional[Player]:
        """Текущий защищающийся игрок."""
        for i in range(1, len(self.players)):
            opponent_index = (self.attacker_index + i) % len(self.players)
            player = self.players[opponent_index]
            if not player.finished_game:
                return player
        return None

    @property
    def support_player(self) -> Optional[Player]:
        """Возвращает игрока, который может подкидывать карты следующим после основного атакующего."""
        active_players = [p for p in self.players if not p.finished_game]
        if len(active_players) < 3:
            return None

        opponent = self.opponent_player
        if not opponent: return None

        try:
            base_index = active_players.index(opponent)
            support_index = (base_index + 1) % len(active_players)
            supporter = active_players[support_index]
            return supporter if supporter != self.current_player else None
        except ValueError:
            return None

    @property
    def allow_support_attack(self) -> bool:
        """Проверяет, можно ли еще подкидывать карты (по общему лимиту карт)."""
        return len(self.attacking_cards) < self.COUNT_CARDS_IN_START

    @property
    def allow_atack(self) -> bool:
        """
        Проверяет, можно ли еще атаковать (подкидывать) в этом раунде.
        
        Учитывает как общий лимит карт, так и количество карт у защищающегося в начале раунда.
        """
        opponent = self.opponent_player
        if not opponent:
            return False
        return len(self.attacking_cards) < self.COUNT_CARDS_IN_START and \
               len(self.attacking_cards) < self.defender_cards_on_round_start

    @property
    def attacker_can_continue(self) -> bool:
        """Проверяет, есть ли у текущего атакующего карты, которые он может подкинуть."""
        attacker = self.current_player
        if not attacker.cards or not self.allow_atack:
            return False
        
        all_field_cards = self.attacking_cards + self.defending_cards
        field_values = {c.value for c in all_field_cards}
        
        if not field_values:
            return True # Поле пусто, атаковать можно любой картой
        return any(card.value in field_values for card in attacker.cards)

    def attack(self, card: Card) -> None:
        """Добавляет атакующую карту на поле."""
        self.field[card] = None

    def defend(self, attacking_card: Card, defending_card: Card) -> None:
        """Добавляет защищающуюся карту на поле, связывая ее с атакующей."""
        self.field[attacking_card] = defending_card

    def _clear_field(self) -> None:
        """Очищает игровое поле, отправляя все карты с него в биту."""
        for atk_card, def_card in self.field.items():
            self.deck.dismiss(atk_card)
            if def_card:
                self.deck.dismiss(def_card)
        self.field.clear()
        self.attack_announce_message_ids.clear()
        self.attack_sticker_message_ids.clear()
        self.round_attackers.clear()

    def take_all_field(self) -> None:
        """Заставляет защищающегося игрока забрать все карты с поля."""
        opponent = self.opponent_player
        if not opponent:
            self._clear_field()
            return

        cards = self.attacking_cards + self.defending_cards
        opponent.add_cards(cards)
        self._clear_field()

    def take_cards_from_deck(self) -> None:
        """
        Раздает карты игрокам из колоды до установленного лимита (6 карт).

        NOTE: Текущая логика раздачи последних карт из колоды, когда их не хватает
        на всех, корректно работает только для двух игроков. Для >2 игроков
        остаток будет распределен не по правилам.
        
        Deals cards to players from the deck up to the established limit (6 cards).

        NOTE: The current logic for dealing the last cards from the deck when there
        are not enough for everyone works correctly only for two players. For >2 players,
        the remainder will not be distributed according to the rules.
        """
        players_in_turn = self.rotate_players(self.players, self.attacker_index)
        active_players_in_turn = [p for p in players_in_turn if not p.finished_game]

        for player in active_players_in_turn:
            needed = max(0, self.COUNT_CARDS_IN_START - len(player.cards))
            if needed > 0:
                try:
                    cards = self.deck.draw_many(needed)
                    player.add_cards(cards)
                except DeckEmptyError:
                    break # Карты в колоде кончились
    
    def _find_next_active_player_index(self, start_index: int) -> int:
        """Находит индекс следующего игрока, который еще не закончил игру."""
        for i in range(1, len(self.players) + 1):
            next_index = (start_index + i) % len(self.players)
            if not self.players[next_index].finished_game:
                return next_index
        
        logger.warning("No active player found to continue.")
        return start_index # Возвращаем исходный, если ничего не найдено

    def turn(self, skip_def: bool = False) -> None:
        """
        Выполняет переход хода.

        Args:
            skip_def (bool): Если False (стандарт), ход переходит к отбившемуся игроку.
                             Если True (игрок взял), ход переходит к следующему игроку
                             после того, кто взял карты.
        
        Executes a turn transition.

        Args:
            skip_def (bool): If False (default), the turn passes to the player who defended.
                             If True (player took cards), the turn passes to the player
                             next after the one who took the cards.
        """
        logger.debug(f"Switching turn. Skip defender: {skip_def}")
        
        if not skip_def: # "Бито", ход переходит к защитнику
            if self.opponent_player:
                self.attacker_index = self.players.index(self.opponent_player)
            else:
                self.attacker_index = self._find_next_active_player_index(self.attacker_index)
        else: # Игрок взял, ход переходит к следующему после него
            defender = self.opponent_player
            if defender:
                defender_index = self.players.index(defender)
                self.attacker_index = self._find_next_active_player_index(defender_index)
            else:
                self.attacker_index = self._find_next_active_player_index(self.attacker_index)

        self.is_pass = False
        self._clear_field()
        self.take_cards_from_deck()
        
        opponent = self.opponent_player
        if opponent:
            self.defender_cards_on_round_start = len(opponent.cards)
        else:
            self.defender_cards_on_round_start = 0
        
        if self.players and self.attacker_index < len(self.players) and not self.current_player.finished_game:
            self.current_player.turn_started = datetime.now()
