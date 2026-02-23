# Описание папки handlers

Этот пакет содержит обработчики для всех входящих обновлений от Telegram (команды, нажатия кнопок, сообщения и т.д.).
Они отвечают за реакцию бота на действия пользователя.

## Структура

- `game/`: Обработчики, связанные непосредственно с игровым процессом (создание, присоединение, ход игры и т.д.).
- `info/`: Обработчики для информационных команд, таких как `/help` и `/stats`.
- `__init__.py`: Объединяет и регистрирует все роутеры из дочерних модулей.
- `card_theme.py`: Обработчик для смены темы карт.
- `game_mode.py`: Обработчик для смены игрового режима.
- `settings.py`: Обработчик для меню настроек.
- `stats.py`: Обработчик для работы со статистикой.

# handlers Folder Description

This package contains handlers for all incoming updates from Telegram (commands, button clicks, messages, etc.).
They are responsible for the bot's reaction to user actions.

## Structure

- `game/`: Handlers directly related to the gameplay (creation, joining, game flow, etc.).
- `info/`: Handlers for informational commands, such as `/help` and `/stats`.
- `__init__.py`: Combines and registers all routers from child modules.
- `card_theme.py`: Handler for changing the card theme.
- `game_mode.py`: Handler for changing the game mode.
- `settings.py`: Handler for the settings menu.
- `stats.py`: Handler for working with statistics.
