# -*- coding: utf-8 -*-
"""
Пакет `logic`

Этот пакет отвечает за всю основную бизнес-логику и механики игры «Дурак».
Он изолирован от Telegram API и содержит только чистый Python-код, 
который управляет состоянием игры, ходами, правилами и взаимодействием игроков.

Ключевые компоненты:
- `game.py`: Основной класс `Game`, управляющий одной игровой сессией.
- `game_manager.py`: Класс `GameManager`, управляющий всеми активными играми в боте.
- `player.py`: Класс `Player`, представляющий игрока в сессии.
- `exceptions.py`: Пользовательские исключения для обработки игровых ошибок.

--------------------------------------------------------------------------------------

Package `logic`

This package is responsible for all the core business logic and mechanics of the "Durak" game.
It is isolated from the Telegram API and contains only pure Python code 
that manages the game state, moves, rules, and player interactions.

Key components:
- `game.py`: The main `Game` class, which manages a single game session.
- `game_manager.py`: The `GameManager` class, which manages all active games in the bot.
- `player.py`: The `Player` class, which represents a player in a session.
- `exceptions.py`: Custom exceptions for handling game-related errors.
"""
