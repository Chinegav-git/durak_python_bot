#!/bin/bash
# RU: Скрипт для остановки всех сервисов, используемых ботом (PostgreSQL и Redis).
# EN: Script to stop all services used by the bot (PostgreSQL and Redis).

# RU: Определение цветов для форматированного вывода в консоль.
# EN: Definition of colors for formatted console output.
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# RU: Вывод стартового сообщения.
# EN: Printing the start message.
echo -e "${YELLOW}Остановка сервисов бота "Дурак"...${NC}"

# RU: Остановка PostgreSQL. Сначала проверяется статус, чтобы избежать ошибок, если сервис уже остановлен.
# EN: Stopping PostgreSQL. The status is checked first to avoid errors if the service is already stopped.
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

# RU: Остановка Redis. Сначала проверяется статус, чтобы избежать ошибок, если сервис уже остановлен.
# EN: Stopping Redis. The status is checked first to avoid errors if the service is already stopped.
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

# RU: Финальное сообщение об успешной остановке всех сервисов.
# EN: Final message about the successful shutdown of all services.
echo -e "${GREEN}Все сервисы остановлены${NC}"
