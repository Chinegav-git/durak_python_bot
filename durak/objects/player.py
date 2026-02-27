# -*- coding: utf-8 -*-
"""
Модуль, определяющий сущность "Игрок".

Module defining the "Player" entity.
"""

from __future__ import annotations

import logging
import typing
from datetime import datetime
from time import time
from typing import List, Optional, Set

from aiogram import types

from config import Config
from .card import Card
from .errors import NotAllowedMove

if typing.TYPE_CHECKING:
    from .game import Game


class Player:
    """
    Представляет игрока, его состояние и его возможные действия в игре.
    Represents a player, their state, and their possible actions in the game.
    """

    def __init__(self, game: 'Game', user: types.User) -> None:
        self.game = game
        self.user = user
        self.cards: List[Card] = []
        self.finished_game: bool = False
        self.anti_cheat: int = int(time())
        self.turn_started: datetime = datetime.now()
        self.waiting_time: int = Config.WAITING_TIME

    @property
    def id(self) -> int:
        return self.user.id

    @property
    def first_name(self) -> str:
        return self.user.first_name

    @property
    def username(self) -> Optional[str]:
        return self.user.username
    
    @property
    def mention(self) -> str:
        """
        Возвращает HTML-форматированную строку для упоминания пользователя в Telegram.
        Returns an HTML-formatted string to mention the user in Telegram.
        """
        return self.user.mention_html(self.user.first_name)

    def add_cards(self, cards: List[Card]):
        """
        Добавляет карты в руку игрока.
        Adds cards to the player's hand.
        """
        self.cards.extend(cards)
        self.cards.sort()

    def leave(self):
        """
        Обрабатывает выход игрока из игры, сбрасывая его карты в биту.
        Handles a player leaving the game by dismissing their cards to the beaten pile.
        """
        for card in self.cards:
            self.game.deck.dismiss(card)
        self.cards.clear()

    def play_attack(self, card: Card):
        """
        Выполняет ход атакующей картой.
        Performs a move with an attacking card.
        """
        if card not in self.playable_card_atk():
            raise NotAllowedMove("You can't play this card")

        self.remove_card(card)
        self.game.attack(card)

    def play_defence(self, attacking_card: Card, defending_card: Card):
        """
        Выполняет ход защищающейся картой.
        Performs a move with a defending card.
        """
        if defending_card not in self.playable_card_def(attacking_card):
            raise NotAllowedMove("You can't play this card")
        
        self.remove_card(defending_card)
        self.game.defend(attacking_card, defending_card)
    
    def playable_card_atk(self) -> Set[Card]:
        """
        Определяет, какими картами игрок может атаковать.
        Determines which cards the player can attack with.
        """
        if not self.game.allow_atack and self.game.field:
            return set()

        if self == self.game.opponent_player:
            return set()

        if not self.game.field:
            return set(self.cards) if self == self.game.current_player else set()

        all_field_cards = self.game.attacking_cards + self.game.defending_cards
        field_values = {c.value for c in all_field_cards if c}
        return {card for card in self.cards if card.value in field_values}

    def playable_card_def(self, atk_card: Optional[Card] = None) -> Set[Card]:
        """
        Определяет, какими картами игрок может защищаться.
        Determines which cards the player can defend with.
        """
        if not atk_card:
            return set()
        return {card for card in self.cards if self.can_beat(atk_card, card)}

    def can_beat(self, atk_card: Card, def_card: Card) -> bool:
        """
        Проверяет, может ли защитная карта побить атакующую.
        Checks if a defending card can beat an attacking card.
        """
        def_value = int(def_card.value)
        atk_value = int(atk_card.value)

        if def_card.suit == self.game.trump:
            return atk_card.suit != self.game.trump or def_value > atk_value
        
        return def_card.suit == atk_card.suit and def_value > atk_value

    def remove_card(self, card: Card):
        """
        Удаляет карту из руки игрока.
        Removes a card from the player's hand.
        """
        try:
            self.cards.remove(card)
        except ValueError:
            logging.warning(f"Attempted to remove card {card} not in player's hand for user {self.id}")
            raise NotAllowedMove(f"Card {card} not in hand")

    def __repr__(self) -> str:
        return f"<Player id={self.id} name='{self.first_name}'>"
    
    def __str__(self) -> str:
        return self.first_name
