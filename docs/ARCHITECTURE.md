# Architecture Document

This document outlines the software architecture of the "PIDKYDNYI 😼" Telegram bot.

## 1. Core Technology Stack
- **Language:** Python 3.11+
- **Telegram Bot Framework:** `aiogram 2.x` (Asynchronous)
- **Database:** `Pony ORM` for SQLite/PostgreSQL.
- **Configuration:** `python-dotenv` and `environs` for managing settings via environment variables.

## 2. Project Structure
The project is organized into a primary Python package `durak/` with a clear separation of concerns.

```
/
|-- durak/
|   |-- db/
|   |   |-- database.py     # Pony ORM models and database initialization.
|   |   `-- user_settings.py # Logic for user-specific settings.
|   |
|   |-- handlers/
|   |   |-- game/           # Handlers for game-related commands and actions.
|   |   `-- info/           # Handlers for informational commands like /help, /stats.
|   |
|   |-- logic/
|   |   |-- game_manager.py # Core service for managing game state and lifecycle.
|   |   |-- actions.py      # Business logic for player actions (attack, defend, take).
|   |   `-- utils.py        # Helper functions.
|   |
|   |-- objects/
|   |   |-- card.py         # Card object representation.
|   |   |-- deck.py         # Deck logic (creation, shuffling).
|   |   |-- game.py         # Game state object.
|   |   `-- player.py       # Player state object.
|
|-- img/                    # Image assets for rendering the game.
|
|-- bot.py                  # Main application entry point.
|-- loader.py               # Aiogram dispatcher and bot instance initialization.
|-- config.py               # Application configuration loading.
|-- requirements.txt        # Python dependencies.
`-- README.md               # Project overview.
```

## 3. Architectural Principles
- **Asynchronous First:** All I/O operations (Telegram API, Database) are built on Python's `async/await` syntax.
- **Separation of Concerns:**
    - **Handlers (`durak/handlers/`):** Responsible only for receiving and parsing user input from Telegram. They call services to perform business logic.
    - **Services (`durak/logic/`):** Contain the core game logic, business rules, and state management. They are independent of the Telegram API. The `do_turn` function in `actions.py` is the central controller for the game's flow, managing turn transitions and win/loss conditions.
    - **Database (`durak/db/`):** Manages data persistence and defines the data models.
- **State Management:** Active game sessions are managed in-memory by the `GameManager` (`logic/game_manager.py`), which is responsible for creating, tracking, and ending games. The core game state for each session is encapsulated within `Game` objects. The database (`durak/db/`) is used for long-term persistence of user statistics and settings.

## 4. Visual Engine
The project includes a visual component using image assets from the `img/` directory, suggesting that it renders game states as images before sending them to the user.
