#!/bin/bash
# Скрипт для управления запуском и остановкой сервисов PostgreSQL и Redis в окружении proot-distro Debian
# /bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Путь к данным PostgreSQL (для версии 13)
PG_DATA="/var/lib/postgresql/13/main"
PG_CTL="/usr/lib/postgresql/13/bin/pg_ctl"
LOG_FILE="/var/log/postgresql/postgresql-13-main.log"

# Проверка, что скрипт запущен от root
if [ "$(id -u)" -ne 0 ]; then
  echo -e "${RED}Этот скрипт должен быть запущен с правами root или через sudo.${NC}"
  exit 1
fi

start_services() {
    # Запуск Redis Server
    echo "Проверка статуса Redis..."
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}Redis уже запущен.${NC}"
    else
        echo "Запуск Redis..."
        if ! redis-server --daemonize yes; then
            echo -e "${RED}Не удалось запустить Redis.${NC}"
        else
            echo -e "${GREEN}Redis успешно запущен.${NC}"
        fi
    fi

    # Запуск PostgreSQL
    echo "Проверка статуса PostgreSQL..."
    if [ -f "$PG_DATA/postmaster.pid" ]; then
        echo -e "${GREEN}PostgreSQL уже запущен.${NC}"
    else
        echo "Запуск PostgreSQL..."
        if ! su - postgres -c "$PG_CTL -D $PG_DATA -l $LOG_FILE start"; then
            echo -e "${RED}Не удалось запустить PostgreSQL.${NC}"
        else
            echo -e "${GREEN}PostgreSQL успешно запущен.${NC}"
        fi
    fi
}

stop_services() {
    # Остановка PostgreSQL
    echo "Остановка PostgreSQL..."
    if ! su - postgres -c "$PG_CTL -D $PG_DATA stop"; then
        echo -e "${RED}Не удалось остановить PostgreSQL.${NC}"
    else
        echo -e "${GREEN}PostgreSQL успешно остановлен.${NC}"
    fi

    # Остановка Redis
    echo "Остановка Redis..."
    # Используем `redis-cli ping` для проверки, нужно ли останавливать
    if redis-cli ping > /dev/null 2>&1; then
        if ! redis-cli shutdown; then
            echo -e "${RED}Не удалось остановить Redis.${NC}"
        else
            echo -e "${GREEN}Redis успешно остановлен.${NC}"
        fi
    else
        echo "Redis не был запущен."
    fi
}

case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    *)
        echo "Использование: $0 {start|stop}"
        exit 1
        ;;
esac

exit 0
