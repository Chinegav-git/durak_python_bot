# Корневая директория проекта

Эта папка является точкой входа в проект и содержит всю кодовую базу, конфигурационные файлы, документацию и скрипты для запуска.

## Структура

-   **`durak/`**: Основной пакет с исходным кодом бота, реализующий всю игровую логику.
    -   **`durak/locales/`**: Файлы переводов для многоязычной поддержки (uk, ru, en).
-   **`documentation/`**: Техническая и пользовательская документация.
-   **`migrations/`**: Файлы миграций базы данных, управляемые `aerich`.
-   **`img/`**: Графические ассеты (изображения карт, логотипы).
-   **`.idx/`**: Конфигурация среды разработки для IDX.
-   **`bot.py`**: Главный скрипт для запуска бота.
-   **`config.py`**: Файл с основными настройками и константами.
-   **`aerich.ini`**: Конфигурация инструмента для миграций `aerich`.
-   **`CHANGELOG.md`**: История всех версий и изменений в проекте.
-   **`LOCALIZATION_GUIDE.md`**: Руководство по системе многоязычности.
-   **`requirements.txt`**: Список зависимостей Python.
-   **Скрипты запуска**: `start.bat` и `start.sh`.

# Project Root Directory

This folder is the entry point of the project and contains the entire codebase, configuration files, documentation, and startup scripts.

## Structure

-   **`durak/`**: The main package with the bot's source code, implementing all game logic.
    -   **`durak/locales/`**: Translation files for multilingual support (uk, ru, en).
-   **`documentation/`**: Technical and user documentation.
-   **`migrations/`**: Database migration files managed by `aerich`.
-   **`img/`**: Graphical assets (card images, logos).
-   **`.idx/`**: Development environment configuration for IDX.
-   **`bot.py`**: The main script to run the bot.
-   **`config.py`**: File with main settings and constants.
-   **`aerich.ini`**: Configuration file for `aerich` migration tool.
-   **`CHANGELOG.md`**: History of all versions and changes in the project.
-   **`LOCALIZATION_GUIDE.md`**: Guide to the multilingual system.
-   **`requirements.txt`**: List of Python dependencies.
-   **Startup Scripts**: `start.bat` and `start.sh`.
