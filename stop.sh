#!/bin/bash
# Скрипт для остановки процесса бота

# Цвета
GREEN='[0;32m'
RED='[0;31m'
NC='[0m' # No Color

BOT_PROCESS_NAME="bot.py"

# Ищем PID процесса
PID=$(pgrep -f $BOT_PROCESS_NAME)

if [ -z "$PID" ]; then
    echo -e "${RED}Процесс бота не найден.${NC}"
    exit 1
else
    echo "Найден процесс бота с PID: $PID. Производится остановка..."
    # Убиваем процесс
    kill $PID
    # Небольшая задержка, чтобы процесс успел завершиться
    sleep 2
    # Проверяем, завершился ли процесс
    if pgrep -f $BOT_PROCESS_NAME > /dev/null; then
        echo -e "${RED}Не удалось остановить процесс. Попробуйте kill -9 $PID.${NC}"
        exit 1
    else
        echo -e "${GREEN}Процесс бота успешно остановлен.${NC}"
    fi
fi

exit 0
