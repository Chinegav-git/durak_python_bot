import os
import importlib
from enum import StrEnum

# --- Enums and Base Dictionaries ---

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

DECK = {
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
}

SUIT = {
    'd': 'CAACAgIAAxkBAAEFiFhi9N6WsmoVGiVCARK0PaEPy1hxIwACEh4AAnTOqEtb-7pItmYVoSkE',
    'h': 'CAACAgIAAxkBAAEFiFpi9N6Zq1VuvqptUTttNQv3aAre9gACSxoAAgnnqEvn34S0p9V4fSkE',
    's': 'CAACAgIAAxkBAAEFiFxi9N6bYVzGDq8wbRH75_4ZblK7sAACchkAAiZkqEuIdmKBktgSYikE',
    'c': 'CAACAgIAAxkBAAEFiF5i9N6ePrpgsVNpA7xD904tUTCjWQACyhoAAlehqUvmgY-dQGLnSikE'
}

SPECIAL = {
    'draw': 'CAACAgIAAxkBAAEFiGBi9N6gipaKIexU7cVWyxcci2juyAACSx0AArAMqEt3c1jfI8dsHikE',
    'info': 'CAACAgIAAxkBAAPTaYqSQpE7QBqI6RxQy1V_f7X8AfQAAt-QAAKZOVlI_g93-bxV3SM6BA',
    'pass': 'CAACAgIAAxkBAAPUaYqSRSdzRqsNYwa_PpuRTyk5pdAAAuGQAAKZOVlIgWO1xu8huGA6BA',
}

# --- Theme Loading ---

THEMES = {}

def load_themes():
    themes_dir = os.path.join(os.path.dirname(__file__), 'decks')
    for filename in os.listdir(themes_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            theme_name = filename[:-3]
            module = importlib.import_module(f'.decks.{theme_name}', package=__package__)
            if hasattr(module, 'THEME'):
                THEMES[theme_name] = module.THEME

load_themes()

# --- Active Theme and Dynamic Dictionaries ---

ACTIVE_THEME = 'classic'  # Default theme

# CARDS is now a dynamic reference to the active theme's cards
CARDS = THEMES.get(ACTIVE_THEME, {})

def get_stickers():
    """Dynamically generate the STICKERS dictionary based on the active theme."""
    # CARDS needs to be explicitly fetched from THEMES based on ACTIVE_THEME
    # This ensures that if ACTIVE_THEME is changed, STICKERS will use the new theme
    CURRENT_CARDS = THEMES.get(ACTIVE_THEME, {})
    return {
        **CURRENT_CARDS.get('normal', {}),
        **CURRENT_CARDS.get('grey', {}),
        **CURRENT_CARDS.get('trump_normal', {}),
        **CURRENT_CARDS.get('trump_grey', {}),
        **DECK,
        **SUIT,
        **SPECIAL
    }

STICKERS = get_stickers()

# --- Card Class and Functions ---

class Card:
    """ This is Card :> """

    def __init__(self, value: Values, suit: Suits) -> None:
        # Normalize to enums to keep comparisons consistent across the codebase
        self.value: Values = value if isinstance(value, Values) else Values(str(value))
        self.suit: Suits = suit if isinstance(suit, Suits) else Suits(str(suit))
        self.sticker_id: str | None = STICKERS.get(repr(self))

    def __str__(self) -> str:
        # Mapping for face cards
        value_map = {
            Values.JACK: 'J',
            Values.QUEEN: 'Q',
            Values.KING: 'K',
            Values.ACE: 'A'
        }
        # Use the mapped letter if it's a face card, otherwise use its own value (e.g., '6', '7')
        value_str = value_map.get(self.value, self.value.value)

        # Mapping for suit icons
        suit_map = {
            Suits.DIAMOND: SuitsIcons.DIAMOND,
            Suits.HEART: SuitsIcons.HEART,
            Suits.CLUB: SuitsIcons.CLUB,
            Suits.SPADE: SuitsIcons.SPADE
        }
        suit_str = suit_map.get(self.suit, '?')

        return f'{value_str} {suit_str}'

    def __repr__(self) -> str:
        return f"{self.value.value}_{self.suit.value}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.value == other.value and self.suit == other.suit

    def __lt__(self, other) -> bool:
        if not isinstance(other, Card):
            raise ValueError(f"{other} is not card. Cannot sorting.")
        # Sort by suit first, then by value within suit
        suit_order = {'d': 0, 'h': 1, 'c': 2, 's': 3}
        self_suit_idx = suit_order.get(self.suit, 4)
        other_suit_idx = suit_order.get(other.suit, 4)

        if self_suit_idx != other_suit_idx:
            return self_suit_idx < other_suit_idx

        # Within same suit, sort by value (numeric)
        return int(self.value) < int(other.value)

    def __hash__(self) -> int:
        return hash((self.value, self.suit))

def from_str(string: str):
    # Accept formats like '6_d', '10_h', 'j_s', 'A♠', 'a_s' etc.
    parts = string.strip().lower().split('_')
    if len(parts) == 2:
        value_part, suit_part = parts
    elif len(parts) == 1:
        # try to separate by non-alphanumeric (e.g. '10s' or 'a♠')
        s = parts[0]
        # last char(s) may be suit symbol or letter
        if s and (s[-1] in ("d", "h", "c", "s") or s[-1] in ''.join(list(SuitsIcons.__members__.values()))):
            value_part = s[:-1]
            suit_part = s[-1]
        else:
            raise ValueError(f'Cannot parse card string: {string}')
    else:
        raise ValueError(f'Cannot parse card string: {string}')

    # Map face letters to Values
    if value_part in ('j', 'jack'):
        value = Values.JACK
    elif value_part in ('q', 'queen'):
        value = Values.QUEEN
    elif value_part in ('k', 'king'):
        value = Values.KING
    elif value_part in ('a', 'ace'):
        value = Values.ACE
    else:
        # numeric values '6','7',...,'10'
        try:
            value = Values(value_part)
        except Exception:
            # try numeric string to matching Values
            for v in Values:
                if v.value == value_part:
                    value = v
                    break
            else:
                raise ValueError(f'Unknown card value: {value_part}')

    # Map suit: accept 'd','h','c','s' or suit icons
    # Try direct by value
    try:
        suit = Suits(suit_part)
    except Exception:
        # try mapping from icons
        icon_to_value = {member.value: name for name, member in SuitsIcons.__members__.items()}
        # suit_part may be an icon like '♠' or a name
        mapped = icon_to_value.get(suit_part)
        if mapped:
            suit = Suits.__members__.get(mapped)
        else:
            # try if suit_part is full name like 'diamond'
            suit = Suits.__members__.get(suit_part.upper())
            if suit is None:
                raise ValueError(f'Unknown suit: {suit_part}')

    return Card(value, suit)
