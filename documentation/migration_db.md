Проверка статуса:

sudo -u postgres sh -c "cd /tmp && /usr/local/pgsql/bin/pg_ctl -D /var/lib/postgresql/data status"

Запуск сервера:

sudo -u postgres sh -c "cd /tmp && /usr/local/pgsql/bin/pg_ctl -D /var/lib/postgresql/data -l /tmp/postgres.log start"

команды миграции:

aerich migrate
aerich upgrade

Создание миграции:

python3 migrate.py migrate

Применение миграции:

python3 migrate.py upgrade


