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
        """Возвращает красивое текстовое представление, например: 'Т ♥'."""
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
    def from_str(cls, string: str) -> "Card":
        """
        Универсальный фабричный метод для создания карты из строки.
        Поддерживает два формата:
        1. Технический (внутренний): "value_suit", например, "14_s" или "k_h".
        2. Визуальный (локализованный): "ValueSuitIcon", например, "Т♠" или "10♥".
        
        Universal factory method to create a card from a string.
        Supports two formats:
        1. Technical (internal): "value_suit", e.g., "14_s" or "k_h".
        2. Visual (localized): "ValueSuitIcon", e.g., "Т♠" or "10♥".
        """
        string = string.strip().lower()

        # Попытка 1: Парсинг технического формата ("14_s")
        # Attempt 1: Parse technical format ("14_s")
        if '_' in string:
            parts = string.split('_')
            if len(parts) == 2:
                value_part, suit_part = parts
                
                value_map = {'j': Values.JACK, 'q': Values.QUEEN, 'k': Values.KING, 'a': Values.ACE}
                value = value_map.get(value_part, Values(value_part) if value_part.isdigit() else None)
                
                if value in Values and suit_part in Suits:
                    return cls(value, Suits(suit_part))

        # Попытка 2: Парсинг визуального формата ("Т♠")
        # Attempt 2: Parse visual format ("Т♠")
        # ИСПРАВЛЕНО: Оригинальный код не мог парсить `callback_data` из-за отсутствия этого блока.
        # FIXED: The original code could not parse `callback_data` due to the absence of this block.
        suit_icon_map = {
            '♦': Suits.DIAMOND, '♥': Suits.HEART, '♣': Suits.CLUB, '♠': Suits.SPADE,
            'd': Suits.DIAMOND, 'h': Suits.HEART, 'c': Suits.CLUB, 's': Suits.SPADE,
        }
        
        value_str_map = {
            '6': Values.SIX, '7': Values.SEVEN, '8': Values.EIGHT, '9': Values.NINE, '10': Values.TEN,
            'в': Values.JACK, 'j': Values.JACK,
            'д': Values.QUEEN, 'q': Values.QUEEN,
            'к': Values.KING, 'k': Values.KING,
            'т': Values.ACE, 'a': Values.ACE
        }

        suit = None
        value_str = string
        
        # Извлекаем масть из конца строки
        # Extract suit from the end of the string
        for icon, suit_enum in suit_icon_map.items():
            if string.endswith(icon):
                suit = suit_enum
                value_str = string[:-len(icon)].strip()
                break
        
        if suit and value_str in value_str_map:
            return cls(value_str_map[value_str], suit)

        raise ValueError(f"Не удалось распознать карту из строки: '{string}' / Could not recognize card from string: '{string}'")
