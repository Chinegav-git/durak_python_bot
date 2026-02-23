
# -*- coding: utf-8 -*-
"""
Пакет `objects`

Этот пакет содержит основные классы данных (модели), которые описывают все 
сущности в игре «Дурак». Эти классы инкапсулируют состояние и поведение 
ключевых игровых объектов.

В отличие от пакета `logic`, который содержит *действия* над игрой, этот пакет
содержит пассивное *представление* самой игры и ее компонентов.

Ключевые компоненты:
- `card.py`: Представление игральной карты, колоды и мастей.
- `player.py`: Класс `Player`, описывающий игрока, его руку и действия.
- `game.py`: Класс `Game`, который является центральной моделью, объединяющей
  всех игроков, колоду, игровое поле и общее состояние сессии.
- `exceptions.py`: Специфичные для игры исключения, которые помогают управлять
  игровыми правилами и ошибками (например, `NotAllowedMove`).

--------------------------------------------------------------------------------------

Package `objects`

This package contains the core data classes (models) that describe all
the entities in the "Durak" game. These classes encapsulate the state and behavior
of the key game objects.

Unlike the `logic` package, which contains *actions* on the game, this package
contains the passive *representation* of the game itself and its components.

Key components:
- `card.py`: Representation of a playing card, deck, and suits.
- `player.py`: The `Player` class, describing a player, their hand, and actions.
- `game.py`: The `Game` class, which is the central model that brings together
  all players, the deck, the playing field, and the overall session state.
- `exceptions.py`: Game-specific exceptions that help manage game rules and
  errors (e.g., `NotAllowedMove`).
"""
