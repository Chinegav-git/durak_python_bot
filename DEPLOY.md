# Инструкция по Развертыванию Проекта на Debian (в Termux)

Этот документ описывает пошаговый процесс развертывания бота на сервере с операционной системой Debian, с акцентом на запуск в окружении Termux `proot-distro`.

---

### **Шаг 1: Подготовка Окружения Debian**

Если Debian не установлен в Termux, используйте `proot-distro`.

```bash
# 1. Установка утилиты для управления окружениями
pkg install proot-distro

# 2. Установка Debian
proot-distro install debian

# 3. Вход в окружение Debian (все последующие команды выполняются здесь)
proot-distro login debian
```

---

### **Шаг 2: Установка Системных Зависимостей**

Необходимо установить Python 3.11, `pip`, `git`, PostgreSQL и Redis.

```bash
# 1. Обновляем список пакетов
apt update && apt upgrade -y

# 2. Устанавливаем Python, pip и git
apt install -y python3.11 python3-pip git

# 3. Устанавливаем сервер PostgreSQL и клиент
# Примечание: Мы устанавливаем конкретную версию (13), чтобы пути совпадали со скриптами.
apt install -y postgresql-13 postgresql-client-13

# 4. Устанавливаем сервер Redis
apt install -y redis-server
```

---

### **Шаг 3: Настройка Базы Данных PostgreSQL**

1.  **Переключитесь на пользователя `postgres`:**
    ```bash
    su - postgres
    ```

2.  **Создайте пользователя и базу данных:**
    ```bash
    # Создаем пользователя (например, durak_user). На вопросы отвечайте 'y'.
    createuser --interactive

    # Создаем базу данных для этого пользователя
    createdb durak_db -O durak_user
    ```

3.  **Назначьте пароль:**
    ```bash
    # Вход в консоль psql
    psql

    # Устанавливаем пароль для нового пользователя
    ALTER USER durak_user WITH PASSWORD 'ваш_супер_надежный_пароль';

    # Выход из psql
    \q
    ```

4.  **Вернитесь в основную сессию:**
    ```bash
    exit
    ```
---

### **Шаг 4: Клонирование и Настройка Проекта**

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
    *   Создайте файл: `nano .env`
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

---

### **Шаг 5: Управление Сервисами и Ботом**

Вместо стандартных команд `service`, которые могут не работать в `proot-distro`, используйте скрипты из репозитория.

1.  **Сделайте скрипты исполняемыми:**
    ```bash
    chmod +x run_services.sh start.sh stop.sh
    ```

2.  **Запуск фоновых сервисов (БД и Redis):**
    *   Этот скрипт запустит PostgreSQL и Redis в фоновом режиме.
    ```bash
    ./run_services.sh start
    ```

3.  **Применение миграций и запуск бота:**
    *   Скрипт `start.sh` автоматически применит миграции базы данных (`aerich upgrade`) и запустит `bot.py`.
    *   **Важно:** Для постоянной работы бота его нужно запускать в `screen` или `tmux`.

    ```bash
    # Установка screen
    apt install screen -y

    # Создание новой сессии screen
    screen -S bot

    # Запуск бота внутри сессии
    ./start.sh

    # Чтобы выйти из сессии, не прерывая ее, нажмите Ctrl+A, затем D
    # Чтобы вернуться в сессию: screen -r bot
    ```

4.  **Остановка бота:**
    *   Чтобы остановить только процесс бота, используйте `stop.sh`.
    ```bash
    ./stop.sh
    ```

5.  **Остановка фоновых сервисов:**
    *   Этот скрипт остановит PostgreSQL и Redis.
    ```bash
    ./run_services.sh stop
    ```

---
