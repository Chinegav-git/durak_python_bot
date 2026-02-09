# Features & Progress

This document tracks the implemented and planned features for the bot.

## Implemented Features

### Game Core
- **New Game Creation:** Users can start a new game lobby via the `/new` command.
- **Joining a Game:** Players can join an existing lobby using a unique game ID or via inline mode.
- **Game Start:** The game can be started by the lobby creator once enough players have joined.
- **Card Deck:** A standard 36-card deck is created and shuffled for each game.
- **Player Hands:** Players receive their initial set of cards.
- **Trump Card:** A trump suit is determined for each game.

### Game Flow
- **Attacking & Defending:** The basic mechanics of attacking and defending are implemented.
- **Taking Cards:** Players can take cards from the table.
- **Passing (Перевод):** The logic for passing the turn appears to be considered.
- **Turn Management:** The bot manages whose turn it is to attack or defend.

### User Interface & Experience
- **Image-Based Rendering:** The game state is rendered as an image, showing the table, cards, and player hands.
- **Command-Based Interaction:** Most actions are performed through Telegram commands (`/new`, `/join`, `/start`).
- **Callback Buttons:** Some actions are likely handled via inline keyboard (callback) buttons.
- **User Settings:** The database includes a table for user-specific settings.

### Administration & Info
- **Help Command (`/help`):** A help command is available.
- **Statistics (`/stats`):** A command to view user statistics is implemented.
- **Player Management:** The game creator can kick players from the lobby.

## Planned / To-Do
- **Full "Passing" Logic:** Ensure the "переводной дурак" logic is fully implemented and bug-free.
- **Game End & Results:** Properly calculate and display game results and update user statistics.
- **Throttling/Anti-Flood:** Implement middleware to prevent users from spamming commands.
- **State Recovery:** Implement Redis for storing active game sessions to recover state after a server restart (as per architectural principles).
- **Localization:** Add support for EN and RU languages, removing hardcoded strings.
- **Visual Modes:** Implement TEXT and HYBRID rendering modes in addition to the GRAPHIC one.
- **Alembic Migrations:** If switching to SQLAlchemy, implement Alembic for database schema migrations.
- **Improved UI/UX:** Enhance the user interface with more intuitive controls and feedback.
