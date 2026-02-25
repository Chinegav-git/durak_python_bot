#!/bin/bash
# Скрипт для встановлення PostgreSQL 13 вручну

echo "Встановлення PostgreSQL 13 з вихідного коду..."

# Встановлення залежностей для компіляції
sudo apt update
sudo apt install -y build-essential libreadline-dev zlib1g-dev libssl-dev libxml2-dev libxslt1-dev libicu-dev

# Завантаження PostgreSQL 13
cd /tmp
wget https://ftp.postgresql.org/pub/source/v13.15/postgresql-13.15.tar.gz
tar -xzf postgresql-13.15.tar.gz
cd postgresql-13.15

# Конфігурація та компіляція (без readline)
./configure --prefix=/usr/local/pgsql --without-readline
make
sudo make install

# Створення користувача postgres
sudo useradd -r -s /bin/bash postgres

# Створення директорій для даних
sudo mkdir -p /usr/local/pgsql/data
sudo chown postgres:postgres /usr/local/pgsql/data

# Ініціалізація бази даних
sudo -u postgres /usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data

echo "PostgreSQL 13 встановлено в /usr/local/pgsql"
echo "Для запуску: sudo -u postgres /usr/local/pgsql/bin/pg_ctl -D /usr/local/pgsql/data -l logfile start"
