# -*- coding: utf-8 -*-
"""
Менеджер тем оформления карт.

Этот модуль отвечает за управление стикерами, которые используются для
визуального представления карт, колоды и действий в Telegram.
"""

import importlib
import logging
from typing import Any, Dict, Optional


class ThemeManager:
    """Singleton-класс для управления темами стикеров."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._themes: Dict[str, Dict[str, Any]] = {}
        self._initialized = True

    def _load_theme(self, theme_name: str) -> None:
        """Динамически загружает модуль темы по ее имени."""
        if theme_name in self._themes:
            return
        
        try:
            # ИСПРАВЛЕНО: Эта логика теперь будет корректно выполняться для 'classic',
            # так как _themes больше не содержит этот ключ при инициализации.
            # FIXED: This logic will now execute correctly for 'classic',
            # as _themes no longer contains this key on initialization.
            module = importlib.import_module(f'.decks.{theme_name}', package='durak.objects')
            self._themes[theme_name] = getattr(module, 'THEME', {})
        except (ImportError, AttributeError):
            # Если кастомная тема не найдена, используем classic как fallback.
            # If a custom theme is not found, use classic as a fallback.
            if theme_name != 'classic':
                self._load_theme('classic')
                self._themes[theme_name] = self._themes.get('classic', {})
            else:
                # Если даже 'classic' не удалось загрузить, это критическая проблема.
                # If even 'classic' fails to load, this is a critical issue.
                logging.critical(f"FATAL: Could not load base theme 'classic'. Inline mode will be broken.")
                self._themes['classic'] = {}

    def get_sticker(self, sticker_key: str, theme_name: str = 'classic', style: Optional[str] = None) -> Optional[str]:
        """Получает ID стикера с учетом темы и стиля."""
        self._load_theme(theme_name)
        theme_dict = self._themes.get(theme_name)

        if not theme_dict:
            return None

        # 1. Поиск стилизованной карты в теме (например, 'grey')
        if style:
            styled_sticker = theme_dict.get(style, {}).get(sticker_key)
            if styled_sticker:
                return styled_sticker

        # 2. Поиск обычной карты в теме (в категории 'normal')
        normal_sticker = theme_dict.get('normal', {}).get(sticker_key)
        if normal_sticker:
            return normal_sticker

        # 3. Поиск специального или suit стикера в теме (кастомные 'pass', 'draw', 'c', 'd', etc.)
        # Сначала ищем в 'SPECIAL', потом в 'SUIT'
        special_sticker = theme_dict.get('SPECIAL', {}).get(sticker_key)
        if special_sticker:
            return special_sticker
            
        suit_sticker = theme_dict.get('SUIT', {}).get(sticker_key)
        if suit_sticker:
            return suit_sticker

        return None

# Глобальный экземпляр менеджера тем
_theme_manager = ThemeManager()

def get_sticker_id(sticker_key: str, theme_name: str = 'classic', style: Optional[str] = None) -> Optional[str]:
    """
    Публичная функция для простого доступа к стикерам.
    """
    return _theme_manager.get_sticker(sticker_key, theme_name, style)
