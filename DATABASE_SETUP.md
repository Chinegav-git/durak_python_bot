# Инструкция по настройке базы данных Durak Bot

## 📋 Обзор

Этот документ описывает процесс настройки базы данных PostgreSQL для бота Durak.

## 🚀 Быстрый старт

### 1. Запуск PostgreSQL и Redis

```bash
# Если используете Docker
docker compose up -d

# Если PostgreSQL установлен локально
# Убедитесь, что сервис запущен
sudo systemctl status postgresql
```

### 2. Создание таблиц базы данных

```bash
# Активируем виртуальное окружение
source venv/bin/activate

# Создаем таблицы
python setup_database.py
```

### 3. Запуск бота

```bash
# Запускаем бота
python bot.py
```

## 🔧 Детальная настройка

### Проверка статуса сервисов

```bash
# Проверка PostgreSQL
ps aux | grep postgres

# Проверка Redis
ps aux | grep redis

# Проверка портов
netstat -tlnp | grep -E ":5432|:6379"
```

### Создание базы данных (если нужно)

```sql
-- Подключаемся к PostgreSQL
psql -U postgres

-- Создаем базу данных
CREATE DATABASE durak_db;

-- Создаем пользователя (если нужно)
CREATE USER chinegav WITH PASSWORD '90874513067';

-- Даем права на базу данных
GRANT ALL PRIVILEGES ON DATABASE durak_db TO chinegav;
```

### Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
# Настройки PostgreSQL
POSTGRES_USER=chinegav
POSTGRES_PASSWORD=90874513067
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=durak_db

# Настройки Redis (если нужно)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# Токен Telegram бота
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
```

## 🗄️ Структура базы данных

После выполнения `setup_database.py` будут созданы следующие таблицы:

### Таблица `users`
- `id` - Telegram ID пользователя (PK)
- `first_name` - Имя пользователя
- `last_name` - Фамилия (опционально)
- `username` - Username в Telegram (опционально)

### Таблица `chats`
- `id` - Telegram ID чата (PK)
- `title` - Название чата
- `type` - Тип чата ('private', 'group', 'supergroup')

### Таблица `games`
- `id` - ID игры (PK)
- `chat` - Ссылка на чат (FK)
- `players` - Игроки (Many-to-Many)
- `status` - Статус игры ('lobby', 'playing', 'finished')

### Таблица `usersettings`
- `user` - Ссылка на пользователя (One-to-One, PK)
- `stats_enabled` - Включена ли статистика
- `games_played` - Количество сыгранных игр
- `wins` - Количество побед
- `cards_played` - Количество сыгранных карт
- `cards_beaten` - Количество отбитых карт
- `cards_attack` - Количество атак

### Таблица `chatsettings`
- `chat` - Ссылка на чат (One-to-One, PK)
- `game_mode` - Режим игры ('p', 't')
- `card_theme` - Тема карт ('classic', и др.)
- `sticker_id_helper` - Включен ли помощник по ID стикеров
- `is_game_active` - Активна ли игра в чате

## 🐛 Устранение проблем

### Ошибка "relation does not exist"
**Причина:** Таблицы не созданы
**Решение:** Выполните `python setup_database.py`

### Ошибка "connection refused"
**Причина:** PostgreSQL не запущен или неверные настройки подключения
**Решение:** Проверьте статус PostgreSQL и настройки в `.env`

### Ошибка "database does not exist"
**Причина:** База данных не создана
**Решение:** Создайте базу данных согласно инструкции выше

### Ошибка "permission denied"
**Причина:** Недостаточно прав у пользователя базы данных
**Решение:** Дайте необходимые права пользователю

## 🔄 Пересоздание таблиц

Если нужно полностью пересоздать структуру БД:

```bash
# Удаляем все таблицы (ВНИМАНИЕ: все данные будут утеряны!)
python setup_database.py --drop-all  # если добавить такую опцию

# Или вручную через psql
psql -U chinegav -d durak_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Затем создаем таблицы заново
python setup_database.py
```

## 📝 Автоматизация

Для автоматического запуска можно использовать скрипт `start.sh`:

```bash
#!/bin/bash
source venv/bin/activate
python setup_database.py  # Создаем таблицы если их нет
python bot.py              # Запускаем бота
```

## ✅ Проверка работоспособности

После настройки базы данных:

1. Запустите бота: `python bot.py`
2. Отправьте команду `/start` в Telegram
3. Проверьте, что бот отвечает и создает записи в БД

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи бота на наличие ошибок
2. Убедитесь, что все сервисы запущены
3. Проверьте настройки подключения в `.env`
4. Просмотрите этот документ для поиска решения
