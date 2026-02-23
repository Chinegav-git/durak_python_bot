# Инструкция по Развертыванию Проекта на Debian

Этот документ описывает пошаговый процесс развертывания бота на сервере с операционной системой Debian (например, в окружении Termux `proot-distro`).

## 1. Подготовка Окружения Debian

Если Debian не установлен (например, в Termux), используйте `proot-distro`:

```bash
# Установка утилиты для управления окружениями
pkg install proot-distro

# Установка Debian
proot-distro install debian

# Вход в окружение Debian
proot-distro login debian
```
Все последующие команды выполняются внутри сессии Debian.

## 2. Установка Системных Зависимостей

Необходимо установить Python 3.11, `pip`, `git`, PostgreSQL и Redis.

```bash
# 1. Обновляем список пакетов
apt update && apt upgrade -y

# 2. Устанавливаем Python, pip и git
apt install -y python3.11 python3-pip git

# 3. Устанавливаем сервер PostgreSQL и клиент
apt install -y postgresql postgresql-client

# 4. Устанавливаем сервер Redis
apt install -y redis-server
```

## 3. Настройка Базы Данных PostgreSQL

1.  **Переключитесь на пользователя `postgres`:**
    ```bash
    su - postgres
    ```

2.  **Создайте пользователя и базу данных:**
    ```bash
    # Создаем пользователя (например, durak_user)
    createuser --interactive

    # Создаем базу данных
    createdb durak_db
    ```

3.  **Назначьте пароль и права:**
    ```bash
    # Вход в консоль psql
    psql

    # Устанавливаем пароль для нового пользователя
    ALTER USER durak_user WITH PASSWORD 'ваш_супер_надежный_пароль';

    # Предоставляем все права на базу данных
    GRANT ALL PRIVILEGES ON DATABASE durak_db TO durak_user;

    # Выход из psql
    \q
    ```

4.  **Вернитесь в основную сессию:**
    ```bash
    exit
    ```

## 4. Запуск Сервисов

Redis обычно стартует автоматически. Проверьте и при необходимости запустите сервисы:

```bash
# Проверка статуса Redis
service redis-server status

# Проверка статуса PostgreSQL
service postgresql status

# Если сервисы не запущены, запустите их:
# service redis-server start
# service postgresql start
```

## 5. Клонирование и Настройка Проекта

1.  **Клонируйте репозиторий:**
    ```bash
    git clone <URL вашего репозитория> /opt/durak_bot
    cd /opt/durak_bot
    ```

2.  **Установите Python-зависимости:**
    ```bash
    pip3 install -r requirements.txt
    ```

3.  **Создайте и заполните файл `.env`:**
    *   Скопируйте пример, если он есть: `cp .env.example .env`
    *   Или создайте новый и откройте его: `nano .env`
    *   Добавьте следующие переменные, подставив свои значения:

    ```env
    BOT_TOKEN=ВАШ_ТОКЕН_БОТА_ОТ_BOTFATHER

    # Настройки базы данных
    DB_USER=durak_user
    DB_PASSWORD=ваш_супер_надежный_пароль
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=durak_db

    # Настройки Redis
    REDIS_HOST=localhost
    REDIS_PORT=6379
    ```

## 6. Применение Миграций Базы Данных

Этот шаг создает все необходимые таблицы в вашей пустой базе данных.

```bash
# Находясь в директории проекта (/opt/durak_bot)
aerich upgrade
```

## 7. Запуск Бота

После выполнения всех шагов запустите бота.

```bash
python3 bot.py
```

### Рекомендация для Постоянной Работы

Чтобы бот продолжал работать после закрытия терминала, используйте `screen` или `tmux`:

```bash
# Установка screen
apt install screen -y

# Создание новой сессии screen
screen -S bot

# Запуск бота внутри сессии
python3 bot.py

# Чтобы выйти из сессии, не прерывая ее, нажмите Ctrl+A, затем D
# Чтобы вернуться в сессию: screen -r bot
```

Также в репозитории есть скрипт `start.sh`, который автоматизирует шаги 6 и 7. Вы можете запустить его после выполнения шагов 1-5:
```bash
chmod +x start.sh
./start.sh
```
