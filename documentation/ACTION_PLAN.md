# План Действий (Action Plan)

Этот документ отслеживает процесс анализа и восстановления оригинальной, правильной игровой логики проекта.

## Процесс Работы / Work Process

1.  **Анализ / Analysis:** Я (ИИ-ассистент) анализирую ключевой файл проекта на предмет логических ошибок, несоответствий и отклонений от предполагаемой архитектуры.
2.  **Отчет / Report:** Я предоставляю отчет о найденных проблемах.
3.  **Запрос Эталона / Reference Request:** **Для успешного восстановления мне требуется, чтобы вы (разработчик) предоставили содержимое "старой", но правильной версии анализируемого файла, если таковая имеется.**
4.  **Восстановление / Restoration:** Получив эталонный код, я интегрирую правильную логику в текущую кодовую базу, соблюдая все стандарты проекта.
5.  **Отметка в Плане / Plan Marking:** После успешного восстановления файла, я отмечаю его в этом плане.

---

## Критические Риски и Зоны Проверки (Critical Risks and Checkpoints)

- [x] **Система Миграций БД (DB Migration System):**
    - [x] Отказ от `aerich` из-за конфликтов версий.
    - [x] Внедрена система ручных миграций через SQL-скрипты.
    - [x] Создан скрипт `init_db.py` для инициализации пустой БД.
    - [x] Процесс задокументирован в `documentation/DATABASE_MIGRATIONS.md`.
- [x] **Сериализация объектов (Serialization):** Реализовать `__getstate__` и `__setstate__` для `Game` и `Player`. Из сериализации исключены объекты aiogram и логгеры.
- [x] **Игровые действия (Game Actions):** Исправить вызовы `play_attack` и `play_defence` в `actions.py` (удален лишний аргумент `game`).
- [x] **Менеджер игры (Game Manager):** Добавлено восстановление циклической ссылки `player.game = self` при десериализации в `Game.__setstate__`.
- [x] **Приватные чаты (Private Chats):** Исправлена ошибка `TelegramBadRequest` при получении администраторов в ЛС (файл `durak/logic/utils.py`).
- [x] **Исправление критических ошибок v1.9.8 (Critical Bug Fixes):**
    - [x] Исправлен AttributeError в `join.py` (обращение к `game.creator`).
    - [x] Исправлен ValidationError (отсутствие `title` и `type` при создании Chat в БД).
    - [x] Исправлен ParseMode в инлайн-режиме (ошибки парсинга сущностей в "Мои карты").

---

## 🛠 Текущие задачи / Current Tasks

### 1. Настройка "Автопас" / "Autopass" Setting (✅ Завершено / Completed)
- [x] **Расширение БД:** Добавлено поле `auto_pass_enabled` в `UserSettings`. / **DB Expansion:** Added `auto_pass_enabled` field to `UserSettings`.
- [x] **Обновление UI настроек:** Добавлена кнопка переключения в меню настроек. / **UI Update:** Added toggle button to the settings menu.
- [x] **Локализация:** Добавлены строки перевода для новой настройки. / **Localization:** Added translation strings for the new setting.
- [x] **Игровая логика:** Автоматический пропуск хода на основе настройки реализован в `durak/logic/actions.py`. / **Game Logic:** Automatic turn skip based on the setting is implemented in `durak/logic/actions.py`.

---

## Чек-лист Восстановления / Restoration Checklist

### Фаза 1: Цикл Игрового Хода / Phase 1: Game Turn Cycle (✅ Завершено)

-   [x] `durak/handlers/inline.py`
-   [x] `durak/logic/result.py`
-   [x] `durak/handlers/game/actions.py`
-   [x] `durak/logic/actions.py`

### Фаза 2: Ядро Игровой Логики / Phase 2: Game Core Logic (✅ Завершено)

-   [x] **`durak/objects/game.py`**
-   [x] `durak/objects/player.py`
-   [x] `durak/objects/deck.py` (проверен, соответствует норме)
-   [x] `durak/objects/card.py` (проверен, соответствует норме)

### Фаза 3: Жизненный Цикл Игры / Phase 3: Game Lifecycle (✅ Завершено)

-   [x] `durak/handlers/game/new.py`
-   [x] `durak/handlers/game/join.py`
-   [x] `durak/handlers/game/start.py`
-   [x] `durak/logic/game_manager.py` (проверен, соответствует норме)
-   [x] `durak/locales/*.json` (проверены, приведены в соответствие)

### Фаза 4: Настройки и Статистика / Phase 4: Settings and Statistics (В процессе / In Progress)

-   [x] `durak/handlers/settings.py` (критические ошибки вызова API в ЛС исправлены)
-   [ ] `durak/handlers/info/stats.py` (восстановление команды `/stats` с использованием новой структуры данных)
-   [ ] `durak/handlers/info/top.py` (восстановление функционала рейтинга `/top` по чату / игре)
-   [ ] **Статистика (Statistics):** Проверить корректность отображения статистики после рефакторинга сериализации.

### Фаза 5: Команды Администрирования / Phase 5: Admin Commands (Планируется / Planned)

-   [ ] Анализ и восстановление функционала для администраторов бота.