#!/bin/bash
# Скрипт для остановки всех сервисов бота

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Остановка сервисов бота "Дурак"...${NC}"

# Остановка PostgreSQL
echo "Остановка PostgreSQL..."
if sudo -u postgres /usr/local/pgsql/bin/pg_ctl status > /dev/null 2>&1; then
    if sudo -u postgres /usr/local/pgsql/bin/pg_ctl stop; then
        echo -e "${GREEN}✓ PostgreSQL остановлена${NC}"
    else
        echo -e "${RED}✗ Ошибка остановки PostgreSQL${NC}"
    fi
else
    echo -e "${YELLOW}PostgreSQL уже была остановлена${NC}"
fi

# Остановка Redis
echo "Остановка Redis..."
if redis-cli ping > /dev/null 2>&1; then
    if redis-cli shutdown; then
        echo -e "${GREEN}✓ Redis остановлен${NC}"
    else
        echo -e "${RED}✗ Ошибка остановки Redis${NC}"
    fi
else
    echo -e "${YELLOW}Redis уже был остановлен${NC}"
fi

echo -e "${GREEN}Все сервисы остановлены${NC}"
