# Інструкція з розгортання та запуску бота 24/7

Цей документ описує, як налаштувати та запустити бота в режимі 24/7, використовуючи **Redis** для керування станом ігор та **Supervisor** для автоматичного керування процесом бота.

## Загальні передумови

Перед початком переконайтеся, що у вашій системі встановлено:
- `git`
- `python3` та `python3-pip`
- `python3-venv` (рекомендовано)

## Варіант 1: Розгортання на стандартному Debian/Ubuntu

Цей сценарій підходить для будь-якого віртуального або фізичного сервера під керуванням Debian або Ubuntu.

### 1. Встановлення Redis та Supervisor

```bash
sudo apt update
sudo apt install -y redis-server supervisor
```
Після встановлення, Redis та Supervisor автоматично запустяться та будуть ввімкнені для старту при завантаженні системи.

### 2. Підготовка проекту

```bash
# Перейдіть до директорії, де ви хочете розмістити бота (наприклад, /var/www/)
cd /var/www/

# Клонуйте репозиторій
git clone https://github.com/Chinegav-git/durak_python_bot.git
cd durak_python_bot

# Створіть та активуйте віртуальне оточення
python3 -m venv venv
source venv/bin/activate

# Встановіть залежності
pip install -r requirements.txt
```

### 3. Налаштування конфігурації

Створіть файл `.env`. Ви можете скопіювати приклад та заповнити його:
```bash
# cp .env.example .env # Якщо є файл-приклад
nano .env
```
Додайте в `.env` ваші дані:
```
BOT_TOKEN=ВАШ_ТОКЕН_БОТА
ADMINS=ВАШ_ТЕЛЕГРАМ_ID
```
Налаштування Redis у `config.py` за замовчуванням (`localhost:6379`) вже підходять для цього сценарію.

### 4. Створення конфігурації для Supervisor

Створіть новий файл конфігурації для вашого бота:
```bash
sudo nano /etc/supervisor/conf.d/durak_bot.conf
```

Вставте в нього наступний вміст. **Не забудьте змінити `your_user` на вашого реального користувача**, від імені якого буде працювати бот.

```ini
[program:durak_bot]
command=/var/www/durak_python_bot/venv/bin/python bot.py
directory=/var/www/durak_python_bot
autostart=true
autorestart=true
stderr_logfile=/var/log/durak_bot.err.log
stdout_logfile=/var/log/durak_bot.out.log
user=your_user
```

### 5. Запуск бота через Supervisor

```bash
# Повідомте Supervisor про новий конфігураційний файл
sudo supervisorctl reread

# Додайте нову програму до списку процесів Supervisor
sudo supervisorctl update

# Запустіть бота (зазвичай він стартує автоматично завдяки autostart=true)
sudo supervisorctl start durak_bot

# Перевірка статусу
sudo supervisorctl status durak_bot
```
Тепер бот працює у фоновому режимі та автоматично перезапуститься у випадку збою.

---

## Варіант 2: Розгортання в Termux (Android)

Цей сценарій дозволяє запустити бота на Android-пристрої, використовуючи Termux.

### 1. Встановлення залежностей в Termux

```bash
pkg update
pkg install -y git python redis

# Встановлюємо supervisor через pip, оскільки його немає в pkg
pip install supervisor
```

### 2. Підготовка проекту

```bash
# Клонуйте репозиторій
git clone https://github.com/Chinegav-git/durak_python_bot.git
cd durak_python_bot

# Встановіть залежності Python
pip install -r requirements.txt
```
*Примітка: Віртуальне оточення в Termux є опціональним.*

### 3. Налаштування конфігурації

Створіть та заповніть файл `.env`, як описано вище.

### 4. Створення конфігурації для Supervisor

Оскільки в Termux немає глобальної директорії для конфігурацій Supervisor, ми створимо її в корені проекту.

Створіть файл `supervisord.conf`:
```bash
nano supervisord.conf
```

Вставте в нього наступний вміст. Ця конфігурація буде керувати як ботом, так і Redis-сервером.

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
```

### 5. Запуск

Для стабільної роботи в Termux потрібно тримати пристрій "активним".

1.  **(Окрема сесія Termux)** Запустіть `termux-wake-lock`, щоб запобігти "засинанню" пристрою.
    ```bash
    termux-wake-lock
    ```

2.  **(Основна сесія Termux)** Перебуваючи в директорії проекту, запустіть Supervisor:
    ```bash
    supervisord -c supervisord.conf
    ```

3.  **Керування та перевірка статусу:**
    ```bash
    # Відкрити консоль керування
    supervisorctl -c supervisord.conf
    
    # Всередині консолі supervisorctl можна використовувати команди:
    # status         (перевірити статус всіх процесів)
    # restart durak_bot  (перезапустити бота)
    # stop all       (зупинити все)
    # exit           (вийти з консолі)
    ```
Бот та Redis тепер працюють у фоновому режимі під керуванням Supervisor.
