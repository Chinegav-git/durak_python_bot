# -*- coding: utf-8 -*-
"""
Скрипт-обертка для запуска Aerich с предварительной загрузкой .env файла.
Wrapper script to run Aerich with .env file preloading.
"""

import sys
from environs import Env

# Загружаем переменные окружения из .env файла
# This step is critical for aerich to "see" the DB settings
env = Env()
env.read_env()

# Теперь, когда окружение настроено, можно запустить aerich
# Now that the environment is set up, we can run aerich
from aerich.cli import cli

if __name__ == "__main__":
    # Мы передаем аргументы командной строки (например, "migrate" или "upgrade")
    # напрямую в функцию cli() из aerich
    # We pass command-line arguments (e.g., "migrate" or "upgrade")
    # directly to the cli() function from aerich
    cli()
