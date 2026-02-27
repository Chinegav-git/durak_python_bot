# Управление Схемой Базы Данных

## Обзор

Этот документ описывает процедуру инициализации и обновления схемы базы данных. Ранее для этих целей использовалась библиотека `aerich`, но из-за неразрешимых конфликтов версий с `tortoise-orm` проект перешел на систему "ручных" миграций и инициализации.

Текущий подход более надежен, так как он зависит исключительно от встроенных и проверенных механизмов `tortoise-orm`.

---

# Database Schema Management

## Overview

This document describes the procedure for initializing and updating the database schema. The `aerich` library was previously used for these purposes, but due to irresolvable version conflicts with `tortoise-orm`, the project has switched to a system of "manual" migrations and initialization.

The current approach is more reliable as it depends solely on the built-in and proven mechanisms of `tortoise-orm`.

---

## 1. Инициализация Базы Данных (на новой машине)

Для создания всех необходимых таблиц с нуля в пустой базе данных, используйте скрипт `init_db.py`.

**Команда:**
```bash
python3 init_db.py
```

Этот скрипт выполнит следующие действия:
1.  Прочитает конфигурацию из `.env`.
2.  Подключится к базе данных.
3.  Вызовет `Tortoise.generate_schemas()`, которая создаст все таблицы на основе моделей, определенных в `durak/db/models.py`.

**Важно:** Этот скрипт предназначен только для первоначальной настройки. Запуск его на существующей базе данных приведет к ошибке, если таблицы уже существуют.

---

## 1. Database Initialization (on a new machine)

To create all necessary tables from scratch in an empty database, use the `init_db.py` script.

**Command:**
```bash
python3 init_db.py
```

This script will perform the following actions:
1.  Read the configuration from `.env`.
2.  Connect to the database.
3.  Call `Tortoise.generate_schemas()`, which will create all tables based on the models defined in `durak/db/models.py`.

**Important:** This script is intended for initial setup only. Running it on an existing database will result in an error if the tables already exist.

---

## 2. Применение Будущих Изменений (Миграции)

Поскольку автоматическая генерация миграций больше не используется, все изменения схемы должны применяться с помощью ручных SQL-скриптов.

**Процесс:**

1.  **Измените Модель:** Внесите необходимые изменения в файл `durak/db/models.py` (например, добавьте новое поле).

2.  **Создайте Скрипт Миграции:** Создайте новый Python-файл в директории `migrations/scripts/`. Имя файла должно отражать его назначение и иметь порядковый номер, например `002_add_user_bio.py`.

3.  **Напишите Код Миграции:** Вставьте в созданный файл код, который выполнит прямое SQL-изменение в базе данных. Ниже приведен шаблон, который можно адаптировать.

### Пример и Шаблон Скрипта Миграции

Допустим, вы добавили поле `bio = fields.TextField(null=True)` в модель `User`.

Ваш скрипт миграции (`migrations/scripts/002_add_user_bio.py`) будет выглядеть так:

```python
# -*- coding: utf-8 -*-
# migrations/scripts/002_add_user_bio.py
"""
Ручная миграция для добавления поля 'bio' в таблицу 'users'.
Manual migration to add the 'bio' field to the 'users' table.
"""

import asyncio
from environs import Env
from tortoise import Tortoise, run_async

# Убедитесь, что переменные окружения загружены
# Ensure environment variables are loaded
Env().read_env()

from durak.db.tortoise_config import TORTOISE_ORM

async def run_migration():
    """
    Выполняет SQL-запрос для изменения схемы.
    Executes the SQL query to alter the schema.
    """
    print("--- Запуск ручной миграции: 002_add_user_bio ---")
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        conn = Tortoise.get_connection("default")

        print("Применяем SQL-изменения...")
        # ПРЯМОЙ SQL ЗАПРОС
        await conn.execute_script(
            '''
            ALTER TABLE "users" ADD COLUMN "bio" TEXT;
            '''
        )
        print("...Успешно.")

    except Exception as e:
        # Если колонка уже существует, это не ошибка
        # If the column already exists, it's not an error
        if "already exists" in str(e):
            print("...Колонка уже существует, пропущено.")
        else:
            print(f"ОШИБКА: {e}")
    finally:
        await Tortoise.close_connections()
        print("--- Миграция завершена ---")

if __name__ == "__main__":
    run_async(run_migration())

```

4.  **Запустите Скрипт:**
    ```bash
    python3 migrations/scripts/002_add_user_bio.py
    ```

Этот подход обеспечивает полный контроль и прозрачность процесса изменения базы данных.

---

## 2. Applying Future Changes (Migrations)

Since automatic migration generation is no longer used, all schema changes must be applied using manual SQL scripts.

**Process:**

1.  **Modify the Model:** Make the necessary changes to the `durak/db/models.py` file (e.g., add a new field).

2.  **Create a Migration Script:** Create a new Python file in the `migrations/scripts/` directory. The filename should reflect its purpose and have a sequence number, e.g., `002_add_user_bio.py`.

3.  **Write the Migration Code:** Insert code into the created file that will execute a direct SQL change in the database. A template is provided below for adaptation.

### Example and Migration Script Template

Suppose you added a `bio = fields.TextField(null=True)` field to the `User` model.

Your migration script (`migrations/scripts/002_add_user_bio.py`) would look like this:

```python
# -*- coding: utf-8 -*-
# migrations/scripts/002_add_user_bio.py
"""
Manual migration to add the 'bio' field to the 'users' table.
"""

import asyncio
from environs import Env
from tortoise import Tortoise, run_async

# Ensure environment variables are loaded
Env().read_env()

from durak.db.tortoise_config import TORTOISE_ORM

async def run_migration():
    """
    Executes the SQL query to alter the schema.
    """
    print("--- Running manual migration: 002_add_user_bio ---")
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        conn = Tortoise.get_connection("default")

        print("Applying SQL changes...")
        # DIRECT SQL QUERY
        await conn.execute_script(
            '''
            ALTER TABLE "users" ADD COLUMN "bio" TEXT;
            '''
        )
        print("...Success.")

    except Exception as e:
        # If the column already exists, it's not an error
        if "already exists" in str(e):
            print("...Column already exists, skipped.")
        else:
            print(f"ERROR: {e}")
    finally:
        await Tortoise.close_connections()
        print("--- Migration finished ---")

if __name__ == "__main__":
    run_async(run_migration())

```

4.  **Run the Script:**
    ```bash
    python3 migrations/scripts/002_add_user_bio.py
    ```

This approach provides full control and transparency over the database modification process.
