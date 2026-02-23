# -*- coding: utf-8 -*-
"""
Модуль, определяющий сущность "Игрок".

Этот модуль содержит класс `Player`, который представляет участника игры.
Класс хранит информацию о пользователе Telegram, его картах в руке,
а также реализует основную логику для выполнения ходов (атака, защита).

--------------------------------------------------------------------------------------

Module defining the "Player" entity.

This module contains the `Player` class, which represents a game participant.
The class stores information about the Telegram user, their hand of cards,
and implements the core logic for performing moves (attack, defense).
"""

from __future__ import annotations

import logging
import typing
from datetime import datetime
from time import time
from typing import List, Optional, Set

from config import Config

# ИСПРАВЛЕНО: Зависимость от `card as c` удалена.
from .card import Card, Suits, Values
from .errors import NotAllowedMove

if typing.TYPE_CHECKING:
    from .game import Game

logger = logging.getLogger(__name__)


class Player:
    """
    Представляет игрока, его состояние и его возможные действия в игре.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя Telegram.
        first_name (str): Имя пользователя.
        username (Optional[str]): Username пользователя в Telegram (если есть).
        cards (List[Card]): Список карт в руке игрока.
        finished_game (bool): Флаг, указывающий, закончил ли игрок игру.
        anti_cheat (int): Временная метка последнего действия для защиты от спама.
        turn_started (datetime): Время начала текущего хода игрока.
        waiting_time (int): Время ожидания хода (из конфигурации).
    
    Represents a player, their state, and their possible actions in the game.

    Attributes:
        id (int): The unique Telegram user ID.
        first_name (str): The user's first name.
        username (Optional[str]): The user's Telegram username (if available).
        cards (List[Card]): The list of cards in the player's hand.
        finished_game (bool): A flag indicating if the player has finished the game.
        anti_cheat (int): Timestamp of the last action for spam protection.
        turn_started (datetime): The start time of the player's current turn.
        waiting_time (int): The time allotted for a turn (from config).
    """

    def __init__(self, user_id: int, first_name: str, username: Optional[str]) -> None:
        self.id: int = user_id
        self.first_name: str = first_name
        self.username: Optional[str] = username
        self.cards: List[Card] = []
        self.finished_game: bool = False
        self.anti_cheat: int = int(time())
        self.turn_started: datetime = datetime.now()
        self.waiting_time: int = Config.WAITING_TIME

    @property
    def mention(self) -> str:
        """
        Возвращает HTML-форматированную строку для упоминания пользователя в Telegram.
        Returns an HTML-formatted string to mention the user in Telegram.
        """
        if self.username:
            return f"<a href='https://t.me/{self.username}'>{self.first_name}</a>"
        return f"<a href='tg://user?id={self.id}'>{self.first_name}</a>"

    def add_cards(self, cards: List[Card]):
        """
        Добавляет карты в руку игрока.
        Adds cards to the player's hand.
        """
        self.cards.extend(cards)
        # Сортируем карты для удобного отображения в инлайн-режиме
        self.cards.sort()

    def leave(self, game: 'Game'):
        """
        Обрабатывает выход игрока из игры, сбрасывая его карты в биту.
        Handles a player leaving the game by dismissing their cards to the beaten pile.
        """
        for card in self.cards:
            game.deck.dismiss(card)
        self.cards.clear()

    def play_attack(self, game: 'Game', card: Card):
        """
        Выполняет ход атакующей картой.

        Проверяет, можно ли играть этой картой, и если да, удаляет ее из руки
        и размещает на игровом поле.
        
        Raises:
            NotAllowedMove: Если ход этой картой запрещен правилами.

        Performs a move with an attacking card.

        Checks if the card can be played, and if so, removes it from the hand
        and places it on the game field.

        Raises:
            NotAllowedMove: If playing this card is forbidden by the rules.
        """
        if card not in self.playable_card_atk(game):
            raise NotAllowedMove("You can't play this card")

        self.remove_card(card)
        game.attack(card)

    def play_defence(self, game: 'Game', attacking_card: Card, defending_card: Card):
        """
        Выполняет ход защищающейся картой.

        Проверяет, можно ли побить атакующую карту выбранной картой, и если да,
        удаляет ее из руки и размещает на поле.

        Raises:
            NotAllowedMove: Если ход этой картой запрещен правилами.

        Performs a move with a defending card.

        Checks if the attacking card can be beaten with the selected card, and if so,
        removes it from the hand and places it on the field.

        Raises:
            NotAllowedMove: If playing this card is forbidden by the rules.
        """
        if defending_card not in self.playable_card_def(game, attacking_card):
            raise NotAllowedMove("You can't play this card")
        
        self.remove_card(defending_card)
        game.defend(attacking_card, defending_card)
    
    def playable_card_atk(self, game: 'Game') -> Set[Card]:
        """
        Определяет, какими картами игрок может атаковать (ходить или подкидывать).

        - Если поле пусто, и это ход игрока, он может ходить любой картой.
        - Если на поле уже есть карты, подкидывать можно только карты тех достоинств,
          которые уже есть на столе (и у атакующих, и у отбивающихся карт).
        - Нельзя подкидывать, если защищающийся отбился и ход окончен (`game.allow_atack`)
        - Защищающийся игрок не может атаковать.

        Returns:
            Множество карт, доступных для атаки.

        Determines which cards the player can attack with (lead or toss in).

        - If the field is empty and it's the player's turn, they can play any card.
        - If there are cards on the field, one can only toss in cards with values
          that are already on the table (both attacking and defending cards).
        - Tossing in is not allowed if the defender has beaten all cards and the turn is over (`game.allow_atack`).
        - The defending player cannot attack.

        Returns:
            A set of cards available for attack.
        """
        if not game.allow_atack and game.field:
            return set()

        if self == game.opponent_player:
            return set()

        if not game.field:
            return set(self.cards) if self == game.current_player else set()

        all_field_cards = game.attacking_cards + game.defending_cards
        field_values = {c.value for c in all_field_cards if c}
        return {card for card in self.cards if card.value in field_values}

    def playable_card_def(self, game: 'Game', atk_card: Optional[Card] = None) -> Set[Card]:
        """
        Определяет, какими картами из руки игрок может побить конкретную атакующую карту.

        Args:
            game (Game): Текущий объект игры.
            atk_card (Optional[Card]): Карта, которую нужно побить.

        Returns:
            Множество карт, которыми можно побить `atk_card`.

        Determines which cards from the player's hand can beat a specific attacking card.

        Args:
            game (Game): The current game object.
            atk_card (Optional[Card]): The card to be beaten.

        Returns:
            A set of cards that can beat `atk_card`.
        """
        if not atk_card:
            return set()
        return {card for card in self.cards if self.can_beat(game, atk_card, card)}

    def card_match(self, card_1: Card, card_2: Card) -> bool:
        """
        Проверяет, совпадают ли достоинства двух карт.
        Checks if two cards have the same value.
        """
        if card_1 is None or card_2 is None:
            return False
        return card_1.value == card_2.value
    
    def can_add_to_field(self, game: 'Game', card: Card) -> bool:
        """
        Проверяет, можно ли подкинуть на стол данную карту (по правилам "подкидывания").
        Checks if a given card can be tossed onto the field (according to "tossing in" rules).
        """
        if self == game.opponent_player:
            return False

        if not game.field:
            return self == game.current_player

        all_field_cards = game.attacking_cards + game.defending_cards
        field_values = {c.value for c in all_field_cards if c}
        return card.value in field_values

    def can_beat(self, game: 'Game', atk_card: Card, def_card: Card) -> bool:
        """
        Проверяет, может ли защитная карта побить атакующую по правилам игры.
        
        ИСПРАВЛЕНО: Эта функция была полностью неработоспособна из-за использования
        удаленного `RANKS`. Теперь она использует прямое сравнение числовых значений
        достоинств карт.

        - Козырная карта бьет любую некозырную карту.
        - Козырная карта бьет козырную карту меньшего достоинства.
        - Некозырная карта бьет карту той же масти и меньшего достоинства.

        Returns:
            bool: True, если `def_card` бьет `atk_card`.

        Checks if a defending card can beat an attacking card according to the game rules.

        FIXED: This function was completely non-functional due to using the removed
        `RANKS`. It now uses direct comparison of the numeric values of the card ranks.

        - A trump card beats any non-trump card.
        - A trump card beats a trump card of a lower rank.
        - A non-trump card beats a card of the same suit and lower rank.

        Returns:
            bool: True if `def_card` beats `atk_card`.
        """
        # Сравниваем карты как целые числа
        def_value = int(def_card.value)
        atk_value = int(atk_card.value)

        # Если защитная карта - козырь
        if def_card.suit == game.trump:
            # Она бьет либо некозырную, либо козырь меньшего достоинства
            return atk_card.suit != game.trump or def_value > atk_value
        
        # Если защитная карта не козырь
        # Она бьет только ту же масть большего достоинства
        return def_card.suit == atk_card.suit and def_value > atk_value

    def remove_card(self, card: Card):
        """
        Удаляет карту из руки игрока.

        Raises:
            NotAllowedMove: Если такой карты нет в руке.
        
        Removes a card from the player's hand.

        Raises:
            NotAllowedMove: If the card is not in the hand.
        """
        try:
            self.cards.remove(card)
        except ValueError:
            logger.warning(f"Attempted to remove card {card} not in player's hand for user {self.id}")
            raise NotAllowedMove(f"Card {card} not in hand")

    def __repr__(self) -> str:
        return f"<Player id={self.id} name='{self.first_name}'>"
    
    def __str__(self) -> str:
        return self.first_name
