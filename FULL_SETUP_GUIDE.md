# Полная инструкция запуску проекту з PostgreSQL, Redis та іншими сервісами

Цей документ містить повну покрокову інструкцію для налаштування та запуску Telegram-бота "Дурак" з усіма необхідними сервісами.

## Архітектура проекту / Project Architecture

### Ключові компоненти / Key Components

#### 1. Система впровадження залежностей / Dependency Injection System
- **GameManagerMiddleware:** Автоматично передає GameManager у всі обробники
- **Розташування:** `durak/middleware/game_manager_middleware.py`
- **Призначення:** Забезпечує єдиний доступ до стану гри

#### 2. Управління callback запитами / Callback Management System  
- **CallbackManager:** Запобігає накопиченню та дублюванню callback'ів
- **Розташування:** `durak/utils/callback_manager.py`
- **Функціональність:**
  - Обмеження одночасних запитів (максимум 10)
  - Запобігання дублюванню (5 хвилин)
  - Автоматичне очищення старих записів

#### 3. Ігровий менеджер / Game Manager
- **GameManager:** Центральний компонент управління ігровими сесіями
- **Розташування:** `durak/logic/game_manager.py`
- **Особливості:** Зберігає стан гри в Redis для швидкого доступу

## Системні вимоги

- **Операційна система:** Linux (Debian/Ubuntu), macOS, або Windows з WSL2
- **Python:** 3.11 або новіший
- **Оперативна пам'ять:** мінімум 512MB, рекомендовано 1GB+
- **Місце на диску:** мінімум 2GB вільного місця

## Варіанти розгортання

### Варіант 1: Docker (Рекомендовано для початківців)

Найпростіший спосіб запуску з усіма сервісами в контейнерах.

#### 1. Встановлення Docker та Docker Compose

**Linux (Debian/Ubuntu):**
```bash
# Встановлення Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Встановлення Docker Compose
sudo apt install docker-compose-plugin

# Додавання користувача до групи docker
sudo usermod -aG docker $USER
newgrp docker
```

**macOS/Windows:** Завантажте Docker Desktop з [docker.com](https://docker.com)

#### 2. Запуск сервісів через Docker Compose

```bash
# Перейдіть до директорії проекту
cd /path/to/durak_python_bot

# Запустіть всі сервіси в фоновому режимі
docker-compose up -d

# Перевірка статусу сервісів
docker-compose ps
```

Сервіси будуть доступні за адресами:
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

#### 3. Налаштування проекту

```bash
# Створіть файл .env
cp .env.example .env
nano .env
```

Заповніть `.env` файл:
```env
BOT_TOKEN=ВАШ_ТОКЕН_БОТА_ОТ_BOTFATHER
ADMINS=ВАШ_ТЕЛЕГРАМ_ID

# Налаштування бази даних (для Docker)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=durak_db
DB_USER=chinegav
DB_PASSWORD=90874513067

# Налаштування Redis (для Docker)
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### 4. Встановлення залежностей та запуск бота

```bash
# Створення віртуального оточення
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# або venv\Scripts\activate  # Windows

# Встановлення залежностей
pip install -r requirements.txt

# Запуск бота
python bot.py
```

---

### Варіант 2: Ручна установка (Linux/Debian/Ubuntu)

#### 1. Встановлення системних залежностей

```bash
# Оновлення системи
sudo apt update && sudo apt upgrade -y

# Встановлення Python та інструментів
sudo apt install -y python3.11 python3-pip python3-venv git

# Встановлення PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Встановлення Redis
sudo apt install -y redis-server

# Встановлення додаткових інструментів
sudo apt install -y build-essential libpq-dev
```

#### 2. Налаштування PostgreSQL

```bash
# Перехід до користувача postgres
sudo -u postgres psql

# Створення бази даних та користувача
CREATE DATABASE durak_db;
CREATE USER chinegav WITH PASSWORD '90874513067';
ALTER USER chinegav CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE durak_db TO chinegav;

# Вихід з psql
\q
```

#### 3. Налаштування Redis

```bash
# Перевірка статусу Redis
sudo systemctl status redis-server

# Якщо Redis не запущено, запустіть його
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Тестування Redis
redis-cli ping
# Повинно повернути: PONG
```

#### 4. Налаштування проекту

```bash
# Клонування репозиторію
git clone https://github.com/Chinegav-git/durak_python_bot.git
cd durak_python_bot

# Створення віртуального оточення
python3 -m venv venv
source venv/bin/activate

# Встановлення Python залежностей
pip install -r requirements.txt

# Створення файлу .env
cp .env.example .env
nano .env
```

Заповніть `.env` файл:
```env
BOT_TOKEN=ВАШ_ТОКЕН_БОТА_ОТ_BOTFATHER
ADMINS=ВАШ_ТЕЛЕГРАМ_ID

# Налаштування бази даних
DB_HOST=localhost
DB_PORT=5432
DB_NAME=durak_db
DB_USER=chinegav
DB_PASSWORD=90874513067

# Налаштування Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### 5. Запуск сервісів та бота

```bash
# Запуск PostgreSQL (якщо не запущено)
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Запуск Redis (якщо не запущено)
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Альтернативно: використовуйте скрипт run_services.sh
chmod +x run_services.sh
sudo ./run_services.sh start

# Запуск бота
python bot.py
```

---

### Варіант 3: Розгортання в Termux (Android)

#### 1. Встановлення залежностей в Termux

```bash
# Оновлення пакетів
pkg update && pkg upgrade -y

# Встановлення необхідних пакетів
pkg install -y git python redis postgresql

# Встановлення supervisor для керування процесами
pip install supervisor
```

#### 2. Налаштування PostgreSQL в Termux

```bash
# Ініціалізація бази даних
initdb $PREFIX/var/lib/postgresql/data

# Запуск PostgreSQL
pg_ctl -D $PREFIX/var/lib/postgresql/data -l logfile start

# Створення бази даних та користувача
createdb durak_db
createuser chinegav
psql -c "ALTER USER chinegav WITH PASSWORD '90874513067';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE durak_db TO chinegav;"
```

#### 3. Налаштування проекту

```bash
# Клонування проекту
git clone https://github.com/Chinegav-git/durak_python_bot.git
cd durak_python_bot

# Встановлення залежностей
pip install -r requirements.txt

# Створення .env файлу
cp .env.example .env
nano .env
```

#### 4. Створення конфігурації Supervisor

Створіть файл `supervisord.conf`:
```bash
nano supervisord.conf
```

Вставте наступний вміст:
```ini
[supervisord]
nodaemon=false

[program:durak_bot]
command=python bot.py
directory=%(here)s
autostart=true
autorestart=true
stderr_logfile=%(here)s/durak_bot.err.log
stdout_logfile=%(here)s/durak_bot.out.log

[program:redis_server]
command=redis-server
autostart=true
autorestart=true
stderr_logfile=%(here)s/redis.err.log
stdout_logfile=%(here)s/redis.out.log

[program:postgres_server]
command=pg_ctl -D $PREFIX/var/lib/postgresql/data -l logfile start
autostart=true
autorestart=true
stderr_logfile=%(here)s/postgres.err.log
stdout_logfile=%(here)s/postgres.out.log
```

#### 5. Запуск

```bash
# Запуск wake-lock для стабільної роботи
termux-wake-lock

# Запуск Supervisor
supervisord -c supervisord.conf

# Перевірка статусу
supervisorctl -c supervisord.conf status
```

---

## Перевірка працездатності

### 1. Перевірка підключення до бази даних

```bash
# PostgreSQL
psql -h localhost -U chinegav -d durak_db -c "SELECT version();"

# Redis
redis-cli ping
```

### 2. Перевірка бота

```bash
# Запуск бота в тестовому режимі
python bot.py

# Перевірка логів на наявність помилок
tail -f durak_bot.out.log
```

## Керування сервісами

### Docker Compose команди

```bash
# Перевірка статусу
docker-compose ps

# Перегляд логів
docker-compose logs -f postgres
docker-compose logs -f redis

# Перезапуск сервісів
docker-compose restart postgres
docker-compose restart redis

# Зупинка всіх сервісів
docker-compose down
```

### Systemd команди (для ручної установки)

```bash
# Статус сервісів
sudo systemctl status postgresql
sudo systemctl status redis-server

# Перезапуск сервісів
sudo systemctl restart postgresql
sudo systemctl restart redis-server

# Логи сервісів
sudo journalctl -u postgresql -f
sudo journalctl -u redis-server -f
```

### Скрипти проекту

```bash
# Запуск сервісів (PostgreSQL + Redis)
sudo ./run_services.sh start

# Зупинка сервісів
sudo ./run_services.sh stop

# Запуск бота
./start.sh

# Зупинка бота
./stop.sh
```

## Налаштування команд бота

Після запуску бота, налаштуйте команди через @BotFather:

1. Відкрийте діалог з @BotFather
2. Надішліть `/mybots` та виберіть вашого бота
3. Натисніть "Edit Bot" → "Edit Commands"
4. Скопіюйте вміст файлу `commands.txt` та надішліть його

## Моніторинг та логи

### Розташування логів

- **Docker:** `docker-compose logs -f [service_name]`
- **Systemd:** `sudo journalctl -u [service_name] -f`
- **Supervisor:** `tail -f durak_bot.out.log`

### Корисні команди моніторингу

```bash
# Перевірка завантаження системи
htop

# Перевірка використання пам'яті
free -h

# Перевірка дискового простору
df -h

# Моніторинг мережевих з'єднань
netstat -tlnp | grep -E '(5432|6379)'
```

## Поширені проблеми та рішення

### Проблема: "Connection refused" до PostgreSQL

**Рішення:**
```bash
# Перевірка статусу PostgreSQL
sudo systemctl status postgresql

# Перевірка конфігурації
sudo nano /etc/postgresql/*/main/postgresql.conf
# Переконайтесь, що listen_addresses = '*'

# Перезапуск PostgreSQL
sudo systemctl restart postgresql
```

### Проблема: "Redis connection failed"

**Рішення:**
```bash
# Перевірка статусу Redis
sudo systemctl status redis-server

# Тестування підключення
redis-cli ping

# Перевірка конфігурації
sudo nano /etc/redis/redis.conf
# Переконайтесь, що bind 127.0.0.1 ::1
```

### Проблема: "Bot token is invalid"

**Рішення:**
1. Перевірте токен у @BotFather
2. Переконайтесь, що токен правильно скопійовано у `.env`
3. Перезапустіть бота

### Проблема: "ModuleNotFoundError: No module named '...'"

**Рішення:**
```bash
# Активуйте віртуальне оточення
source venv/bin/activate

# Перевстановіть залежності
pip install -r requirements.txt

# Перевірте встановлення
pip list
```

## Оновлення проекту

```bash
# Отримання останніх змін
git pull origin main

# Оновлення залежностей
pip install -r requirements.txt --upgrade

# Застосування міграцій бази даних
aerich upgrade

# Перезапуск бота
./stop.sh && ./start.sh
```

## Резервне копіювання

### База даних PostgreSQL

```bash
# Створення резервної копії
pg_dump -h localhost -U chinegav durak_db > backup_$(date +%Y%m%d).sql

# Відновлення з резервної копії
psql -h localhost -U chinegav durak_db < backup_20231201.sql
```

### Redis

```bash
# Створення резервної копії
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb backup_redis_$(date +%Y%m%d).rdb

# Відновлення
redis-cli FLUSHALL
redis-cli RESTORE backup_redis_20231201.rdb
```

---

## Контакти та підтримка

Якщо у вас виникли проблеми з установкою або запуском:

1. Перевірте логи на наявність помилок
2. Зверніться до документації в `documentation/`
3. Створіть issue в GitHub репозиторії

**Важливо:** Зберігайте ваш `.env` файл в безпеці і ніколи не передавайте його третім особам!
