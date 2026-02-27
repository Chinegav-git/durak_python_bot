# -*- coding: utf-8 -*-
"""
Диагностический скрипт для проверки инициализации Tortoise ORM.
Diagnostic script to test Tortoise ORM initialization.
"""

import asyncio
from environs import Env

async def run_test():
    """Tries to initialize Tortoise ORM and reports status."""
    print("--- Запуск диагностики Tortoise ORM ---")
    
    # 1. Загрузка переменных окружения
    # 1. Loading environment variables
    print("\n1. Загрузка файла .env...")
    try:
        env = Env()
        env.read_env()
        print("   ...Файл .env успешно загружен.")
    except Exception as e:
        print(f"   ❌ ОШИБКА: Не удалось загрузить .env: {e}")
        return

    # 2. Импорт конфигурации
    # 2. Importing configuration
    print("\n2. Импорт конфигурации TORTOISE_ORM...")
    try:
        from durak.db.tortoise_config import TORTOISE_ORM
        from tortoise import Tortoise
        print("   ...Конфигурация успешно импортирована.")
    except ImportError as e:
        print(f"   ❌ ОШИБКА: Не удалось импортировать конфигурацию: {e}")
        print("   Проверьте, что вы запускаете скрипт из корневой папки проекта.")
        return

    # 3. Попытка инициализации
    # 3. Attempting initialization
    print("\n3. Инициализация Tortoise ORM...")
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        print("   ✅ УСПЕХ: Tortoise ORM успешно инициализирован.")
        
        if Tortoise.apps:
            print(f"   Найденные приложения Tortoise: {list(Tortoise.apps.keys())}")
        else:
            print("   ⚠️ ПРЕДУПРЕЖДЕНИЕ: Tortoise.apps пусто после инициализации.")
            
    except Exception as e:
        print(f"   ❌ КРИТИЧЕСКАЯ ОШИБКА во время инициализации:")
        print(f"   Тип ошибки: {type(e).__name__}")
        print(f"   Детали: {e}")
    finally:
        await Tortoise.close_connections()
        print("\n--- Диагностика завершена ---")

if __name__ == "__main__":
    asyncio.run(run_test())
