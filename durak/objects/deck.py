# -*- coding: utf-8 -*-
"""
Модуль, определяющий сущность "Колода".

Этот модуль содержит класс `Deck`, который представляет собой игральную колоду.
Он отвечает за создание, тасование, раздачу карт и определение козыря.

--------------------------------------------------------------------------------------

Module defining the "Deck" entity.

This module contains the `Deck` class, which represents a playing card deck.
It is responsible for creating, shuffling, dealing cards, and determining the trump suit.
"""

import logging
from random import shuffle
from typing import List, Optional

# ИСПРАВЛЕНО: Импорты сделаны более явными для улучшения читаемости.
from .card import Card, Suits, SuitsIcons, Values
from .errors import DeckEmptyError


class Deck:
    """Представляет игральную колоду карт для игры в "Дурака"."""

    def __init__(self) -> None:
        self.cards: List[Card] = []
        self.beaten: List[Card] = []
        self.trump: Optional[Suits] = None
        self.trump_ico: Optional[SuitsIcons] = None
        self.logger = logging.getLogger(__name__)

    def shuffle(self) -> None:
        """
        Тасует карты в колоде в случайном порядке.
        
        Shuffles the cards in the deck randomly.
        """
        self.logger.debug('Shuffling Deck')
        shuffle(self.cards)

    def draw(self) -> Card:
        """
        Берет одну карту с верха колоды.

        Raises:
            DeckEmptyError: Если колода пуста.

        Returns:
            Объект Card.

        Draws one card from the top of the deck.

        Raises:
            DeckEmptyError: If the deck is empty.

        Returns:
            A Card object.
        """
        try:
            card = self.cards.pop()
            self.logger.debug(f'Drawing card: {str(card)}')
            return card
        except IndexError:
            raise DeckEmptyError()

    def draw_many(self, count: int) -> List[Card]:
        """
        Берет указанное количество карт из колоды.

        Если в колоде меньше карт, чем запрошено, вернет все, что есть.

        Args:
            count (int): Количество карт для взятия.

        Returns:
            Список объектов Card.

        Draws a specified number of cards from the deck.

        If the deck has fewer cards than requested, it returns what is available.

        Args:
            count (int): The number of cards to draw.

        Returns:
            A list of Card objects.
        """
        cards_to_draw = []
        for _ in range(count):
            try:
                cards_to_draw.append(self.draw())
            except DeckEmptyError:
                break  # Останавливаемся, если карты в колоде закончились
        return cards_to_draw

    def dismiss(self, card: Card):
        """
        Перемещает карту в стопку отбитых (в биту).

        Args:
            card (Card): Карта, которую нужно убрать в биту.
        
        Moves a card to the beaten pile.

        Args:
            card (Card): The card to be moved to the beaten pile.
        """
        self.beaten.append(card)

    def _set_trump(self):
        """
        Определяет козырь по последней карте в колоде и устанавливает его иконку.
        ИСПРАВЛЕНО: Добавлена проверка на пустую колоду для предотвращения ошибки IndexError.
        
        Determines the trump from the last card in the deck and sets its icon.
        FIXED: Added a check for an empty deck to prevent an IndexError.
        """
        if not self.cards:
            self.logger.warning("Attempted to set trump on an empty deck.")
            return

        self.trump = self.cards[-1].suit
        
        # ИСПРАВЛЕНО: Логика определения иконки упрощена и сделана более надежной.
        suit_to_icon_map = {
            Suits.DIAMOND: SuitsIcons.DIAMOND,
            Suits.HEART: SuitsIcons.HEART,
            Suits.CLUB: SuitsIcons.CLUB,
            Suits.SPADE: SuitsIcons.SPADE,
        }
        self.trump_ico = suit_to_icon_map.get(self.trump)
        self.logger.info(f"New trump is {self.trump.name} ({self.trump_ico})")

    def _clear(self):
        """
        Очищает колоду, биту и сбрасывает козырь.
        
        Clears the deck, the beaten pile, and resets the trump.
        """
        self.cards.clear()
        self.beaten.clear()
        self.trump = None
        self.trump_ico = None

    def _fill_cards(self):
        """
        Заполняет колоду стандартным набором из 36 карт, тасует и определяет козырь.
        
        Fills the deck with a standard set of 36 cards, shuffles it, and sets the trump.
        """
        self._clear()

        for value in Values:
            for suit in Suits:
                # ИСПРАВЛЕНО: В конструктор Card передаются сами объекты Enum, а не их значения.
                self.cards.append(Card(value, suit))

        self.shuffle()
        self._set_trump()
        
        # self.cards = self.cards[:2]  # for test
