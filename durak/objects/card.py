import os
import importlib
from enum import StrEnum
from typing import Dict, Optional, Any

# --- Enums ---

class Suits(StrEnum):
    DIAMOND: str = 'd'
    HEART: str = 'h'
    CLUB: str = 'c'
    SPADE: str = 's'

class SuitsIcons(StrEnum):
    DIAMOND: str = '♦'
    HEART: str = '♥'
    CLUB: str = '♣'
    SPADE: str = '♠'

class Values(StrEnum):
    SIX: str = '6'
    SEVEN: str = '7'
    EIGHT: str = '8'
    NINE: str = '9'
    TEN: str = '10'
    JACK: str = '11'
    QUEEN: str = '12'
    KING: str = '13'
    ACE: str = '14'

# --- Theme Management ---

class ThemeManager:
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
        if theme_name not in self._themes:
            try:
                module = importlib.import_module(f'.decks.{theme_name}', package=__package__)
                self._themes[theme_name] = getattr(module, 'THEME', {})
            except (ImportError, AttributeError):
                if theme_name != 'classic': # Avoid infinite recursion
                    self._load_theme('classic') # Load classic as fallback
                    self._themes[theme_name] = self._themes.get('classic', {})
                else:
                    self._themes['classic'] = {}

    def get_sticker(self, sticker_key: str, theme_name: str = 'classic', style: Optional[str] = None) -> Optional[str]:
        # Ensure the theme is loaded, including the classic fallback
        self._load_theme(theme_name)
        if theme_name not in self._themes:
             theme_name = 'classic' # Should be loaded by _load_theme

        # Try to get a styled card from the theme
        if style:
            theme_dict = self._themes.get(theme_name, {})
            return theme_dict.get(style, {}).get(sticker_key)

        # If no style, try to get a special sticker from the theme first
        theme_dict = self._themes.get(theme_name, {})
        special_sticker = theme_dict.get('SPECIAL', {}).get(sticker_key)
        if special_sticker:
            return special_sticker

        # Fallback to base special stickers
        return self._base_stickers.get('SPECIAL', {}).get(sticker_key) or \
               self._base_stickers.get('DECK', {}).get(sticker_key) or \
               self._base_stickers.get('SUIT', {}).get(sticker_key)

_theme_manager = ThemeManager()

def get_sticker_id(sticker_key: str, theme_name: str = 'classic', style: Optional[str] = None) -> Optional[str]:
    return _theme_manager.get_sticker(sticker_key, theme_name, style)

# --- Card Class and Functions ---

class Card:
    def __init__(self, value: Values, suit: Suits) -> None:
        self.value: Values = value if isinstance(value, Values) else Values(str(value))
        self.suit: Suits = suit if isinstance(suit, Suits) else Suits(str(suit))

    def __str__(self) -> str:
        value_map = {Values.JACK: 'J', Values.QUEEN: 'Q', Values.KING: 'K', Values.ACE: 'A'}
        value_str = value_map.get(self.value, self.value.value)
        suit_map = {Suits.DIAMOND: SuitsIcons.DIAMOND, Suits.HEART: SuitsIcons.HEART, Suits.CLUB: SuitsIcons.CLUB, Suits.SPADE: SuitsIcons.SPADE}
        suit_str = suit_map.get(self.suit, '?')
        return f'{value_str} {suit_str}'

    def __repr__(self) -> str:
        return f"{self.value.value}_{self.suit.value}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Card): return NotImplemented
        return self.value == other.value and self.suit == other.suit

    def __lt__(self, other) -> bool:
        if not isinstance(other, Card): raise ValueError(f"{other} is not card.")
        suit_order = {'d': 0, 'h': 1, 'c': 2, 's': 3}
        self_suit_idx = suit_order.get(self.suit, 4)
        other_suit_idx = suit_order.get(other.suit, 4)
        if self_suit_idx != other_suit_idx:
            return self_suit_idx < other_suit_idx
        return int(self.value) < int(other.value)

    def __hash__(self) -> int:
        return hash((self.value, self.suit))

def from_str(string: str):
    parts = string.strip().lower().split('_')
    if len(parts) == 2:
        value_part, suit_part = parts
    elif len(parts) == 1:
        s = parts[0]
        if s and (s[-1] in ('d', 'h', 'c', 's') or s[-1] in ''.join(list(SuitsIcons.__members__.values()))):
            value_part, suit_part = s[:-1], s[-1]
        else: raise ValueError(f'Cannot parse card string: {string}')
    else: raise ValueError(f'Cannot parse card string: {string}')

    value_map = {'j': Values.JACK, 'q': Values.QUEEN, 'k': Values.KING, 'a': Values.ACE}
    value = value_map.get(value_part, Values(value_part) if value_part.isdigit() else None)
    if value is None:
        raise ValueError(f'Unknown card value: {value_part}')

    suit_map_rev = {v.value: k for k, v in SuitsIcons.__members__.items()}
    suit_name = suit_map_rev.get(suit_part, suit_part).upper()
    suit = Suits[suit_name] if suit_name in Suits.__members__ else Suits(suit_part)

    return Card(value, suit)
