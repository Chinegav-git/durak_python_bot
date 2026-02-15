from __future__ import annotations
from datetime import datetime
from time import time
from aiogram import types
from typing import List, Optional

import logging
import typing

from . import card as c
from .errors import (DeckEmptyError)

from config import Config

if typing.TYPE_CHECKING:
    from .game import Game
    from .card import Card


class Player:
    """ This is Player"""

    def __init__(self, game: Game, user: types.User) -> None:
        self.user: types.User = user  # User obj | from Aiogram
        self.game: Game = game  # Game obj
        self.cards: List[Card] = list()
        self.finished_game: bool = False # Player status
        self.logger = logging.getLogger(__name__)
        self.anti_cheat: int = int(time())
        self.turn_started: datetime = datetime.now()
        self.waiting_time: int = Config.WAITING_TIME


    def draw_cards_from_deck(self):
        """ Take the missing number of cards from the deck """
        lack = max(0, self.game.COUNT_CARDS_IN_START - len(self.cards))
        if lack == 0:
            return
            
        try:
            cards_to_draw = self.game.deck.draw_many(lack)
            self.add_cards(cards_to_draw)
        except DeckEmptyError:
            self.logger.warning(f'DeckEmptyError for player {self.user.id}')


    def add_cards(self, cards: List[Card]):
        """ Add cards in hands """
        self.cards += cards


    def leave(self):
        """ Cleaning self (Cards) """
        for card in self.cards:
            self.game.deck.dismiss(card)
        self.cards.clear()


    def play_attack(self, card: Card):
        """ Plays a card and removes it from hand """
        self.remove_card(card)
        self.game.attack(card)


    def play_defence(self, attacking_card: Card, defending_card: Card):
        self.remove_card(defending_card)
        self.game.defend(attacking_card, defending_card)
    

    def playable_card_atk(self) -> List[Card]:
        """ Returns a list of cards the player can legally attack with. """
        playable: List[Card] = []
        game = self.game
        
        # The `can_add_to_field` method correctly handles all logic, including
        # who is allowed to attack (not the defender) and who can start (main attacker).
        if not game.allow_atack and not game.field:
             return [] # Can't attack if limit is reached (unless it's the very first move)

        for card in self.cards:
            if self.can_add_to_field(card):
                playable.append(card)

        return playable
    

    def playable_card_def(self, atk_card: Optional[Card] = None) -> List[Card]:
        playable: List[Card] = []

        for card in self.cards:
            if self.can_beat(atk_card, card):
                playable.append(card)

        return playable


    def card_match(self, card_1: Card, card_2: Card) -> bool:
        if card_1 is None or card_2 is None:
            return False
        return card_1.value == card_2.value
    

    def can_add_to_field(self, card: Card) -> bool:
        """ Determines if the player can add a specific card to the field. """
        # The defender can never add cards.
        if self == self.game.opponent_player:
            return False

        field = self.game.field

        # If the field is empty, only the main attacker can start.
        if not field:
            return self == self.game.current_player

        # If the field is not empty, any non-defender can add a card if it matches rank.
        all_field_cards = self.game.attacking_cards + self.game.defending_cards
        field_values = {c.value for c in all_field_cards if c}

        return card.value in field_values


    def can_beat(self, atk_card: Card, def_card: Card) -> bool:
        if def_card.suit == self.game.trump:
            return ( atk_card.suit != self.game.trump ) or ( def_card.value > atk_card.value )
        
        elif ( def_card.suit == atk_card.suit ):
            return def_card.value > atk_card.value
        
        else:
            return False


    def remove_card(self, card: Card):
        if card in self.cards:
            self.cards.remove(card)
        else:
            self.logger.warning(f"Attempted to remove card {card} not in player's hand for user {self.user.id}")

    def __repr__(self) -> str:
        return repr(self.user)
    

    def __str__(self) -> str:
        return str(self.user)