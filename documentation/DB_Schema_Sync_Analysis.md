# Статический анализ синхронизации схемы БД

Этот документ описывает результат статического анализа кодовой базы по состоянию на 24.07.2024.

## Общий вывод

Программный код на уровне Python является внутренне согласованным. Зависимости между модулями и конфигурациями выглядят корректными.

Однако существует **фундаментальный архитектурный разрыв между программной логикой (Code Layer) и физическим состоянием внешней системы (PostgreSQL)**.

Код *ожидает*, что таблицы `user`, `chat`, `game`, `chatsetting` существуют, но они еще не были созданы в базе данных. Любая функция в коде, которая пытается выполнить операцию чтения или записи в базу данных, неизбежно приведет к сбою `UndefinedTableError` на уровне драйвера БД.

Это не ошибка в логике Python, а отсутствие необходимого шага в настройке инфраструктуры, который синхронизирует ожидания кода с реальностью базы данных.

## Детальный анализ

### 1. Анализ слоя данных (Data Layer)

Этот слой состоит из трех ключевых компонентов, которые должны работать согласованно:

*   **Компонент А: Модели (`durak/db/models.py`)**
    *   **Назначение:** Описывает *ожидаемую* структуру данных в виде Python-классов (`User`, `Chat`, `Game`, `ChatSetting`). Это является "чертежом" вашей базы данных.

*   **Компонент Б: Конфигурация ORM (`durak/db/tortoise_config.py`)**
    *   **Назначение:** "Мост" между кодом и базой данных. Переменная `TORTOISE_ORM` указывает, где находятся "чертежи" моделей.

*   **Компонент В: Конфигурация миграций (`pyproject.toml`)**
    *   **Назначение:** "Мост" для инструмента `aerich`. Указывает `aerich`, где находится конфигурация ORM.

**Вывод по слою данных:** На уровне кода эти три компонента **согласованы** и правильно ссылаются друг на друга.

### 2. Анализ потока данных при взаимодействии с БД

#### Сценарий: Изменение настроек чата (команда `/settings`)

1.  **Компонент:** `durak/handlers/settings.py` получает запрос.
2.  **Взаимодействие:** Код выполняет вызов `await ChatSetting.get_or_create(...)`.
3.  **Трансляция в SQL:** `Tortoise ORM` генерирует SQL-запрос `SELECT ... FROM "chatsetting" WHERE id=...`.
4.  **ТОЧКА СБОЯ:** SQL-запрос отправляется в PostgreSQL. Сервер возвращает ошибку `UndefinedTableError`, поскольку таблицы `"chatsetting"` не существует.

#### Сценарий: Начало новой игры (команда `/new`)

1.  **Компонент:** `durak/logic/game_manager.py` пытается обновить статус игры в БД.
2.  **Взаимодействие:** Код вызывает обновление модели `ChatSetting`.
3.  **Трансляция в SQL:** `Tortoise ORM` генерирует `UPDATE "chatsetting" SET ...`.
4.  **ТОЧКА СБОЯ:** По той же причине PostgreSQL ответит ошибкой, поскольку таблицы `"chatsetting"` не существует.

### Рекомендация

Для устранения этого разрыва необходимо выполнить процесс миграции базы данных с помощью `aerich`, чтобы создать физические таблицы, соответствующие определенным моделям.

---

# Static Analysis of DB Schema Synchronization

This document describes the result of a static analysis of the codebase as of 2024-07-24.

## Overall Conclusion

The Python code level is internally consistent. Dependencies between modules and configurations appear correct.

However, there is a **fundamental architectural gap between the program logic (Code Layer) and the physical state of the external system (PostgreSQL)**.

The code *expects* the tables `user`, `chat`, `game`, `chatsetting` to exist, but they have not yet been created in the database. Any function in the code that attempts to perform a read or write operation to the database will inevitably lead to an `UndefinedTableError` failure at the DB driver level.

This is not a bug in the Python logic, but the absence of a necessary step in the infrastructure setup that synchronizes the code's expectations with the database's reality.

## Detailed Analysis

### 1. Data Layer Analysis

This layer consists of three key components that must work in concert:

*   **Component A: Models (`durak/db/models.py`)**
    *   **Purpose:** Describes the *expected* data structure in the form of Python classes (`User`, `Chat`, `Game`, `ChatSetting`). This is the "blueprint" of your database.

*   **Component B: ORM Configuration (`durak/db/tortoise_config.py`)**
    *   **Purpose:** The "bridge" between the code and the database. The `TORTOISE_ORM` variable indicates where the model "blueprints" are located.

*   **Component C: Migration Configuration (`pyproject.toml`)**
    *   **Purpose:** The "bridge" for the `aerich` tool. It tells `aerich` where the ORM configuration is located.

**Conclusion on the data layer:** At the code level, these three components are **consistent** and correctly reference each other.

### 2. Data Flow Analysis during DB Interaction

#### Scenario: Changing chat settings (command `/settings`)

1.  **Component:** `durak/handlers/settings.py` receives a request.
2.  **Interaction:** The code executes the call `await ChatSetting.get_or_create(...)`.
3.  **Translation to SQL:** `Tortoise ORM` generates the SQL query `SELECT ... FROM "chatsetting" WHERE id=...`.
4.  **POINT OF FAILURE:** The SQL query is sent to PostgreSQL. The server returns an `UndefinedTableError` because the `"chatsetting"` table does not exist.

#### Scenario: Starting a new game (command `/new`)

1.  **Component:** `durak/logic/game_manager.py` attempts to update the game status in the DB.
2.  **Interaction:** The code calls for an update of the `ChatSetting` model.
3.  **Translation to SQL:** `Tortoise ORM` generates `UPDATE "chatsetting" SET ...`.
4.  **POINT OF FAILURE:** For the same reason, PostgreSQL will respond with an error because the `"chatsetting"` table does not exist.

### Recommendation

To bridge this gap, it is necessary to perform a database migration process using `aerich` to create the physical tables that correspond to the defined models.
