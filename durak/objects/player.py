from __future__ import annotations
from datetime import datetime
from time import time
from typing import List, Optional, Set
import logging
import typing

from . import card as c
from .errors import DeckEmptyError, NotAllowedMove
from config import Config

if typing.TYPE_CHECKING:
    from .game import Game
    from .card import Card

logger = logging.getLogger(__name__)

class Player:
    """ This is Player"""

    def __init__(self, user_id: int, first_name: str, username: Optional[str]) -> None:
        self.id: int = user_id
        self.first_name: str = first_name
        self.username: Optional[str] = username
        self.cards: List[Card] = list()
        self.finished_game: bool = False
        self.anti_cheat: int = int(time())
        self.turn_started: datetime = datetime.now()
        self.waiting_time: int = Config.WAITING_TIME

    @property
    def mention(self) -> str:
        """ Returns a string to mention the user in a message. """
        if self.username:
            return f"<a href='https://t.me/{self.username}'>{self.first_name}</a>"
        return f"<a href='tg://user?id={self.id}'>{self.first_name}</a>"

    def add_cards(self, cards: List[Card]):
        """ Add cards in hands """
        self.cards += cards

    def leave(self, game: Game):
        """ Cleaning self (Cards) """
        for card in self.cards:
            game.deck.dismiss(card)
        self.cards.clear()

    def play_attack(self, game: Game, card: Card):
        if card not in self.playable_card_atk(game):
            raise NotAllowedMove("You can't play this card")

        self.remove_card(card)
        game.attack(card)

    def play_defence(self, game: Game, attacking_card: Card, defending_card: Card):
        if defending_card not in self.playable_card_def(game, attacking_card):
            raise NotAllowedMove("You can't play this card")
        
        self.remove_card(defending_card)
        game.defend(attacking_card, defending_card)
    
    def playable_card_atk(self, game: Game) -> Set[Card]:
        if not game.allow_atack and game.field:
            return set()

        if self == game.opponent_player:
            return set()

        if not game.field:
            if self == game.current_player:
                return set(self.cards)
            else:
                return set()

        all_field_cards = game.attacking_cards + game.defending_cards
        field_values = {c.value for c in all_field_cards if c}
        return {card for card in self.cards if card.value in field_values}

    def playable_card_def(self, game: Game, atk_card: Optional[Card] = None) -> Set[Card]:
        if not atk_card:
            return set()
        return {card for card in self.cards if self.can_beat(game, atk_card, card)}

    def card_match(self, card_1: Card, card_2: Card) -> bool:
        if card_1 is None or card_2 is None:
            return False
        return card_1.value == card_2.value
    
    def can_add_to_field(self, game: Game, card: Card) -> bool:
        if self == game.opponent_player:
            return False

        if not game.field:
            return self == game.current_player

        all_field_cards = game.attacking_cards + game.defending_cards
        field_values = {c.value for c in all_field_cards if c}
        return card.value in field_values

    def can_beat(self, game: Game, atk_card: Card, def_card: Card) -> bool:
        def_card_rank = c.RANKS.get(def_card.value)
        atk_card_rank = c.RANKS.get(atk_card.value)

        if not def_card_rank or not atk_card_rank:
            return False

        if def_card.suit == game.trump:
            return (atk_card.suit != game.trump) or (def_card_rank > atk_card_rank)
        elif def_card.suit == atk_card.suit:
            return def_card_rank > atk_card_rank
        else:
            return False

    def remove_card(self, card: Card):
        try:
            self.cards.remove(card)
        except ValueError:
            logger.warning(f"Attempted to remove card {card} not in player's hand for user {self.id}")
            raise NotAllowedMove(f"Card {card} not in hand")

    def __repr__(self) -> str:
        return f"<Player id={self.id} name='{self.first_name}'>"
    
    def __str__(self) -> str:
        return self.first_name
