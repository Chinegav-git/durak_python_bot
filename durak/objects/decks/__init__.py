import os
import importlib

# Получаем путь к текущей директории
package_dir = os.path.dirname(__file__)

# Ищем все файлы .py в директории, кроме __init__.py
for filename in os.listdir(package_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        # Формируем имя модуля для импорта
        module_name = f".{filename[:-3]}"
        # Динамически импортируем модуль
        importlib.import_module(module_name, package=__package__)
