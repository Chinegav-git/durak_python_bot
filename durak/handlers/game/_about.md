# Обработчики Игрового Процесса

### Описание
Эта директория является ключевой частью **Слоя Представления** и содержит все обработчики `aiogram`, отвечающие непосредственно за игровой процесс. Каждый файл в этой директории реализует логику для конкретной команды или игрового действия, начиная от создания лобби и заканчивая обработкой хода игрока.

### Назначение
- **Изоляция логики:** Разделение обработчиков на отдельные файлы по их назначению (`new.py`, `join.py`, `start.py` и т.д.) делает код более читаемым и простым для поддержки.
- **Обработка действий пользователя:** Эти обработчики принимают команды (например, `/new`, `/kick`), нажатия на инлайн-кнопки ("Присоединиться", "Начать игру") и инлайн-запросы (выбор карты для хода), запуская соответствующую бизнес-логику из **Слоя Бизнес-логики** (`durak/logic`).

### Взаимосвязи
- **Вызывается из:** `bot.py` (через `durak/handlers/__init__.py`), который регистрирует все роутеры из этой директории.
- **Использует:**
    - `durak/logic/game_manager.py`: Для получения доступа к состоянию игры и управления им.
    - `durak/logic/actions.py`: Для выполнения конкретных игровых действий (атака, защита, пас).
    - `durak/logic/result.py`: Для формирования визуального ответа в инлайн-режиме (карты, кнопки).
    - `durak/logic/utils.py`: Для проверки прав доступа (создатель, администратор).

---

## Файлы-обработчики / Handler Files

- **`new.py`**
    - **RU:** Обрабатывает команду `/new` для создания игрового лобби в чате.
    - **EN:** Handles the `/new` command to create a game lobby in the chat.

- **`join.py`**
    - **RU:** Обрабатывает команду `/join` и нажатие на кнопку "Присоединиться", позволяя пользователям войти в лобби.
    - **EN:** Handles the `/join` command and the "Join" button press, allowing users to enter the lobby.

- **`start.py`**
    - **RU:** Обрабатывает команду `/start` и нажатие на кнопку "Начать игру" для запуска игрового процесса.
    - **EN:** Handles the `/start` command and the "Start Game" button press to begin the game.

- **`leave.py`**
    - **RU:** Обрабатывает команду `/leave`, позволяя игроку покинуть игру или лобби в текущем чате.
    - **EN:** Handles the `/leave` command, allowing a player to leave the game or lobby in the current chat.

- **`global_leave.py`**
    - **RU:** Обрабатывает команду `/gleave`, позволяя игроку покинуть любую игру, в которой он участвует, из любого чата (например, из ЛС с ботом).
    - **EN:** Handles the `/gleave` command, allowing a player to leave any game they are participating in from any chat (e.g., from a private chat with the bot).

- **`kick.py`**
    - **RU:** Обрабатывает команду `/kick` (в ответ на сообщение) для исключения игрока из активной игры. Доступно создателю или администратору.
    - **EN:** Handles the `/kick` command (in reply to a message) to remove a player from an active game. Available to the creator or an admin.

- **`lobby_kick.py`**
    - **RU:** Обрабатывает нажатие на инлайн-кнопку для исключения игрока из лобби до начала игры. Доступно только создателю.
    - **EN:** Handles an inline button press to kick a player from the lobby before the game starts. Available only to the creator.

- **`kill.py`**
    - **RU:** Обрабатывает команду `/kill` для принудительного завершения игры. Доступно создателю или администратору.
    - **EN:** Handles the `/kill` command to forcibly terminate a game. Available to the creator or an admin.

- **`auto_leave.py`**
    - **RU:** Автоматически исключает игрока из игры, если он покидает чат или был кикнут из него.
    - **EN:** Automatically removes a player from the game if they leave or are kicked from the chat.

- **`close.py`**
    - **RU:** (Временно отключен) Обработчик для закрытия лобби, которое запретит присоединение новых игроков.
    - **EN:** (Temporarily disabled) Handler for closing the lobby to prevent new players from joining.

- **`actions.py`**
    - **RU:** Устаревший обработчик для игровых действий (ход картой, "взять", "пас") через текстовые команды и старые кнопки. Сохранен для обратной совместимости или рефакторинга.
    - **EN:** Legacy handler for game actions (card moves, "take", "pass") via text commands and old buttons. Preserved for backward compatibility or refactoring.

- **`test_win.py`**
    - **RU:** Отладочная команда `/test_win` для администраторов, позволяющая мгновенно завершить игру с объявлением победителя.
    - **EN:** Admin debug command `/test_win` to instantly end the game by declaring a winner.

- **`game_callback.py`**
    - **RU:** Определяет фабрику `GameCallback` (CallbackData) для стандартизации данных, передаваемых всеми игровыми инлайн-кнопками.
    - **EN:** Defines the `GameCallback` factory (CallbackData) to standardize the data passed by all in-game inline buttons.
