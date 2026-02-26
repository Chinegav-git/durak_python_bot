# -*- coding: utf-8 -*-
"""
Модуль, определяющий основные игровые сущности: Карту, Масть и Достоинство.

Этот модуль предоставляет классы для представления игральных карт и их атрибутов.
Он является фундаментом для всей игровой логики.

Ключевые компоненты:
- `Suits`, `Values`: Перечисления (Enum) для мастей и достоинств карт, 
  обеспечивающие строгую типизацию и консистентность.
- `SuitsIcons`: Перечисление для текстовых иконок мастей (♥, ♦, ♣, ♠).
- `Card`: Основной класс, представляющий одну игральную карту. Он включает
  методы для сравнения, строкового представления и хеширования.
- `from_str`: Фабричная функция для создания объекта `Card` из его строкового
  представления (например, "14_s" для туза пик).

--------------------------------------------------------------------------------------

Module defining the core game entities: Card, Suit, and Value.

This module provides classes for representing playing cards and their attributes.
It serves as the foundation for all game logic.

Key components:
- `Suits`, `Values`: Enumerations (Enum) for card suits and values,
  ensuring strong typing and consistency.
- `SuitsIcons`: Enumeration for text icons of suits (♥, ♦, ♣, ♠).
- `Card`: The main class representing a single playing card. It includes
  methods for comparison, string representation, and hashing.
- `from_str`: A factory function for creating a `Card` object from its string
  representation (e.g., "14_s" for the Ace of Spades).
"""

from enum import StrEnum


# --- Перечисления для мастей и достоинств --- #
# --- Enumerations for suits and values --- #

class Suits(StrEnum):
    """Масти карт (внутреннее представление)."""
    DIAMOND = 'd'  # Бубны
    HEART = 'h'    # Червы
    CLUB = 'c'     # Трефы
    SPADE = 's'    # Пики

class SuitsIcons(StrEnum):
    """Иконки мастей для отображения в тексте."""
    DIAMOND = '♦'
    HEART = '♥'
    CLUB = '♣'
    SPADE = '♠'

class Values(StrEnum):
    """Достоинства карт (внутреннее представление, числовое для сравнения)."""
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = '10'
    JACK = '11'   # Валет
    QUEEN = '12'  # Дама
    KING = '13'   # Король
    ACE = '14'    # Туз


# --- Основной класс Карты --- #
# --- Main Card Class --- #

class Card:
    """Представляет одну игральную карту с мастью и достоинством."""
    def __init__(self, value: Values, suit: Suits) -> None:
        self.value: Values = value if isinstance(value, Values) else Values(str(value))
        self.suit: Suits = suit if isinstance(suit, Suits) else Suits(str(suit))

    def __str__(self) -> str:
        """Возвращает красивое текстовое представление, например: 'A ♥'."""
        value_map = {Values.JACK: 'В', Values.QUEEN: 'Д', Values.KING: 'К', Values.ACE: 'Т'}
        value_str = value_map.get(self.value, self.value.value)
        suit_map = {Suits.DIAMOND: SuitsIcons.DIAMOND, Suits.HEART: SuitsIcons.HEART, Suits.CLUB: SuitsIcons.CLUB, Suits.SPADE: SuitsIcons.SPADE}
        suit_str = suit_map.get(self.suit, '?')
        return f'{value_str}{suit_str}'

    def __repr__(self) -> str:
        """Возвращает внутреннее строковое представление, например: '14_h'."""
        return f"{self.value.value}_{self.suit.value}"

    def __eq__(self, other) -> bool:
        """Две карты равны, если у них одинаковые масть и достоинство."""
        if not isinstance(other, Card): return NotImplemented
        return self.value == other.value and self.suit == other.suit

    def __lt__(self, other) -> bool:
        """Сравнение для сортировки. Сначала по масти, потом по достоинству."""
        if not isinstance(other, Card): raise ValueError(f"{other} - это не карта.")
        # Порядок мастей для стабильной сортировки
        suit_order = {'d': 0, 'h': 1, 'c': 2, 's': 3} 
        self_suit_idx = suit_order.get(self.suit, 4)
        other_suit_idx = suit_order.get(other.suit, 4)
        if self_suit_idx != other_suit_idx:
            return self_suit_idx < other_suit_idx
        return int(self.value) < int(other.value)

    def __hash__(self) -> int:
        """Хеш для использования карты в качестве ключа словаря или в множестве."""
        return hash((self.value, self.suit))


    @classmethod
    def from_repr(cls, value: str) -> "Card":
        """
        Восстанавливает объект `Card` из внутреннего строкового представления,
        возвращаемого `__repr__`, например: "14_h".
        
        Restores a `Card` instance from its internal string representation
        returned by `__repr__`, e.g.: "14_h".
        """
        # Используем существующую фабричную функцию для единообразного парсинга.
        return from_str(value)

def from_str(string: str) -> 'Card':
    """
    Фабричная функция для создания карты из ее строкового представления.
    
    Примеры:
    - from_str("14_s") -> Card(ACE, SPADE)
    - from_str("k_h") -> Card(KING, HEART)
    
    Raises:
        ValueError: Если строка имеет неверный формат.
    
    Factory function to create a card from its string representation.
    """
    parts = string.strip().lower().split('_')
    if len(parts) != 2:
        raise ValueError(f'Неверный формат строки для карты: {string}')

    value_part, suit_part = parts

    # Преобразование буквенных значений (J, Q, K, A)
    value_map = {'j': Values.JACK, 'q': Values.QUEEN, 'k': Values.KING, 'a': Values.ACE}
    value = value_map.get(value_part, Values(value_part) if value_part.isdigit() else None)
    
    if value is None or value not in Values:
        raise ValueError(f'Неизвестное достоинство карты: {value_part}')

    # Преобразование масти
    if suit_part not in Suits:
        raise ValueError(f'Неизвестная масть карты: {suit_part}')
    
    suit = Suits(suit_part)

    return Card(value, suit)
