from random import shuffle
from typing import List, Optional
import logging

from . import card as c
from .card import Card
from .errors import DeckEmptyError


class Deck:
    """ This is Deck (cards) """

    def __init__(self) -> None:
        self.cards: List[Card] = list()
        self.beaten: List[Card] = list()
        self.trump: Optional[c.Suits] = None
        self.trump_ico: Optional[c.SuitsIcons] = None
        self.logger = logging.getLogger(__name__)


    def shuffle(self) -> None:
        self.logger.debug('Shuffling Deck')
        shuffle(self.cards)


    def draw(self):
        try:
            card = self.cards.pop()
            self.logger.debug(f'Drawing card: {str(card)}')
            return card
        
        except IndexError:
            raise DeckEmptyError()

    def draw_many(self, count: int) -> List[Card]:
        cards_to_draw = []
        for _ in range(count):
            try:
                cards_to_draw.append(self.draw())
            except DeckEmptyError:
                break  # Stop if the deck runs out of cards
        return cards_to_draw


    def dismiss(self, card: Card):
        self.beaten.append(card)


    def _set_trump(self):
        # Set trump only if not already set (protect from changing during game)
        if self.trump is None:
            self.trump = self.cards[-1].suit
            value_to_key = {member.value: member.name for member in c.Suits}
            self.trump_ico = c.SuitsIcons.__members__.get(value_to_key.get(self.trump))

    def _clear(self):
        self.cards.clear()
        self.beaten.clear()
        self.trump = None


    def _fill_cards(self):
        # Fill deck

        self._clear()

        for value in c.Values:
            for suit in c.Suits:
                self.cards.append(Card(value.value, suit.value))

        self.shuffle()
        self._set_trump()
        
        # self.cards = self.cards[:2]  # for test