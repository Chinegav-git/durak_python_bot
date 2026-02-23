# -*- coding: utf-8 -*-
"""
Менеджер тем оформления карт.

Этот модуль отвечает за управление стикерами, которые используются для
визуального представления карт, колоды и действий в Telegram.

Ключевые компоненты:
- `ThemeManager`: Singleton-класс, который загружает темы из файлов
  в директории `durak/objects/decks/` и предоставляет доступ к ID стикеров.
- `get_sticker_id`: Публичная функция для получения ID стикера по ключу.

Логика тем отделена от `card.py`, чтобы не смешивать модель данных (что такое карта)
с ее представлением (как карта выглядит в виде стикера).

--------------------------------------------------------------------------------------

Card Theme Manager.

This module is responsible for managing the stickers used for the visual
representation of cards, the deck, and actions in Telegram.

Key components:
- `ThemeManager`: A singleton class that loads themes from files
  in the `durak/objects/decks/` directory and provides access to sticker IDs.
- `get_sticker_id`: A public function to get a sticker ID by its key.

The theme logic is separated from `card.py` to avoid mixing the data model
(what a card is) with its presentation (how a card looks as a sticker).
"""

import importlib
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
        # Базовые стикеры, используются как fallback и для общих элементов
        self._base_stickers = {
            'DECK': {
                '24': 'CAACAgIAAxkBAAEFiGZi9N7ml8OK63WgrpmMHTRgGig5_QACajEAAurFqUvJj2venJlh-ykE',
                '23': 'CAACAgIAAxkBAAEFiGhi9N7o92kNdMXkhb2UfweSEGlbXwACdhoAAjgEqUtL9be3AAFMnG8pBA',
                '22': 'CAACAgIAAxkBAAEFiGpi9N7sooqZzKtCZW89_Sv_aKV-5QAC7BgAAi9XqUtZt-xqgqKIJykE',
                '21': 'CAACAgIAAxkBAAEFiGxi9N7yUll7W7ZmTgpooIkCIUL1fAACjhwAAgoFoUs1flPjxcdFnykE',
                '20': 'CAACAgIAAxkBAAEFiG5i9N70gKs1K9kWn-QHAhY8662FaAACgiEAAm8pqEsEMqtOrCBGfykE',
                '19': 'CAACAgIAAxkBAAEFiHBi9N73eDqFJvn5OOXSVfy6UJiTrwACuRwAAobcqEsR6nxQkLIIzSkE',
                '18': 'CAACAgIAAxkBAAEFiHJi9N76c_u64pxf5eaGlb9fkr1WBgAC4yAAAojvoUu2abq95MiYwSkE',
                '17': 'CAACAgIAAxkBAAEFiHRi9N77ow6i_0sZoHBM0ObjLVCQtAACKhoAApbGqUshQpVhJK8zXCkE',
                '16': 'CAACAgIAAxkBAAEFiHZi9N7-Mw0Jy8WJhMFIX1RBGZFN5QACxxkAAq-QqEuNUGFC3PkrHCkE',
                '15': 'CAACAgIAAxkBAAEFiHhi9N8AATKFDzMiVcMjf_XzuZfpqi4AAtkdAAJ1F6FLTqgSwiJAEgIpBA',
                '14': 'CAACAgIAAxkBAAEFiHpi9N8P-kCdlohIccffAkZh1bCgmgAC8xoAAvZPqUthA7mOz0a2eikE',
                '13': 'CAACAgIAAxkBAAEFiHxi9N8RnWrBV0zj9kKCNj0P3qaOVwACcxwAAgv-oEu-N3v6rXvnkSkE',
                '12': 'CAACAgIAAxkBAAEFiH5i9N8VqDKMFhYJXfuaXOJgEboNwwACPRoAAt_CqEsUZjTKvkygaykE',
                '11': 'CAACAgIAAxkBAAEFiIBi9N8adBXRIEPJNcdbiRlxvEwgZgACKyAAAjkVoEuqnZg977o_hCkE',
                '10': 'CAACAgIAAxkBAAEFiIJi9N8d54Lgw6Vo2p9q9BjqV_9MzwACpxgAArDUqEspPQWzJNBpfSkE',
                '9': 'CAACAgIAAxkBAAEFiIRi9N8eqh2_Le9O6muNrZFaXCBb1wACFhwAAhVkqUvqmhH7Y0ldMykE',
                '8': 'CAACAgIAAxkBAAEFiIZi9N8h-zxgl-3snGe7VuMn2MZ_GwACPhsAAhAaoUt_B5QuBqQXrykE',
                '7': 'CAACAgIAAxkBAAEFiIhi9N8jXSfVin1IjP05aoks0PL7kAACthgAAjqNqUuVGexlQC53oSkE',
                '6': 'CAACAgIAAxkBAAEFiIpi9N8lU1OU-1pLUcsvSYHLSzV89gACux0AAm2dqEs6JkjsXDcYNikE',
                '5': 'CAACAgIAAxkBAAEFiIxi9N8ojcOMVjjzQpUYEZ6SA9xeGgACFhwAAny7qEs8fWmbYcuIOykE',
                '4': 'CAACAgIAAxkBAAEFiI5i9N8qyEvAuwPivPPeeySTD2xhQwACxSQAAi5ToUs8oWopzG9drSkE',
                '3': 'CAACAgIAAxkBAAEFiJBi9N8tcMFseyK4lswN-2zWnR0s6wACLxsAAiKvqUubqRWLS5k_cSkE',
                '2': 'CAACAgIAAxkBAAEFiJJi9N8vRPRbcpVSssdeMaMylKGvZAACgB8AAumuoEsHvMBNK8vmDykE',
                '1': 'CAACAgIAAxkBAAEFiJRi9N8yv7HbZ-1qGyWPRvw2BIRdHgACaRwAAoG2qEtzwGDgXspCrCkE',
                '0': 'CAACAgIAAxkBAAEFiJZi9N80NlE-7XBC8xgcL3pAWM1wGgACahsAAoAvqUsv_wNGhQ7GKCkE'
            },
            'SUIT': {
                'd': 'CAACAgIAAxkBAAEFiFhi9N6WsmoVGiVCARK0PaEPy1hxIwACEh4AAnTOqEtb-7pItmYVoSkE',
                'h': 'CAACAgIAAxkBAAEFiFpi9N6Zq1VuvqptUTttNQv3aAre9gACSxoAAgnnqEvn34S0p9V4fSkE',
                's': 'CAACAgIAAxkBAAEFiFxi9N6bYVzGDq8wbRH75_4ZblK7sAACchkAAiZkqEuIdmKBktgSYikE',
                'c': 'CAACAgIAAxkBAAEFiF5i9N6ePrpgsVNpA7xD904tUTCjWQACyhoAAlehqUvmgY-dQGLnSikE'
            },
            'SPECIAL': {
                'draw': 'CAACAgIAAxkBAAEFiGBi9N6gipaKIexU7cVWyxcci2juyAACSx0AArAMqEt3c1jfI8dsHikE',
                'info': 'CAACAgIAAxkBAAPTaYqSQpE7QBqI6RxQy1V_f7X8AfQAAt-QAAKZOVlI_g93-bxV3SM6BA',
                'pass': 'CAACAgIAAxkBAAPUaYqSRSdzRqsNYwa_PpuRTyk5pdAAAuGQAAKZOVlIgWO1xu8huGA6BA',
            }
        }
        self._initialized = True

    def _load_theme(self, theme_name: str) -> None:
        """Динамически загружает модуль темы по ее имени."""
        if theme_name in self._themes:
            return
        
        try:
            # Загружаем модуль из `durak.objects.decks.{theme_name}`
            module = importlib.import_module(f'.decks.{theme_name}', package='durak.objects')
            self._themes[theme_name] = getattr(module, 'THEME', {})
        except (ImportError, AttributeError):
            # Если тема не найдена, используем "classic" как fallback
            if theme_name != 'classic':
                self._load_theme('classic')
                self._themes[theme_name] = self._themes.get('classic', {})
            else:
                self._themes['classic'] = {}

    def get_sticker(self, sticker_key: str, theme_name: str = 'classic', style: Optional[str] = None) -> Optional[str]:
        """Получает ID стикера с учетом темы и стиля."""
        self._load_theme(theme_name)

        # 1. Поиск стилизованной карты в теме (например, серая или козырная)
        if style:
            theme_dict = self._themes.get(theme_name, {})
            styled_sticker = theme_dict.get(style, {}).get(sticker_key)
            if styled_sticker: 
                return styled_sticker

        # 2. Поиск специального стикера в теме (например, своя иконка "паса")
        theme_dict = self._themes.get(theme_name, {})
        special_sticker = theme_dict.get('SPECIAL', {}).get(sticker_key)
        if special_sticker:
            return special_sticker

        # 3. Fallback: поиск в базовых (classic) стикерах
        return self._base_stickers.get('SPECIAL', {}).get(sticker_key) or \
               self._base_stickers.get('DECK', {}).get(sticker_key) or \
               self._base_stickers.get('SUIT', {}).get(sticker_key)

# Глобальный экземпляр менеджера тем
_theme_manager = ThemeManager()

def get_sticker_id(sticker_key: str, theme_name: str = 'classic', style: Optional[str] = None) -> Optional[str]:
    """
    Публичная функция для простого доступа к стикерам.
    
    Args:
        sticker_key: Ключ стикера (например, "13_h" для короля червей, "pass", "draw").
        theme_name: Название темы (например, "classic").
        style: Стиль карты (например, "grey", "trump_normal").
        
    Returns:
        ID файла стикера для Telegram или None, если не найден.
    """
    return _theme_manager.get_sticker(sticker_key, theme_name, style)
