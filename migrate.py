
import asyncio
import sys
from environs import Env

# Загружаем переменные окружения из .env файла
# Этот шаг критически важен, чтобы aerich "увидел" настройки БД
env = Env()
env.read_env()

# Теперь, когда окружение настроено, можно запустить aerich
from aerich.cli import cli

if __name__ == "__main__":
    # Мы передаем аргументы командной строки (например, "migrate" или "upgrade")
    # напрямую в функцию cli() из aerich
    # sys.argv[0] - это имя самого скрипта, поэтому мы его пропускаем
    cli()
