Проверка статуса:

sudo -u postgres sh -c "cd /tmp && /usr/local/pgsql/bin/pg_ctl -D /var/lib/postgresql/data status"

Запуск сервера:

sudo -u postgres sh -c "cd /tmp && /usr/local/pgsql/bin/pg_ctl -D /var/lib/postgresql/data -l /tmp/postgres.log start"

export POSTGRES_USER="chinegav"
export POSTGRES_PASSWORD="90874513067"
export POSTGRES_HOST="127.0.0.1"
export POSTGRES_PORT="5432"
export POSTGRES_DB="durak_db"

команды миграции:

aerich migrate
aerich upgrade

Создание миграции:

python3 migrate.py migrate

Применение миграции:

python3 migrate.py upgrade


