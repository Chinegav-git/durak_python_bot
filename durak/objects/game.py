from datetime import datetime
from aiogram import types
from typing import Any, List, Dict, Optional
import logging

from . import card as c
from .deck import Deck
from .player import Player
from .card import Card

from config import Config


class Game:
    """ This is Game """

    def __init__(self, chat: types.Chat, creator: types.User) -> None:
        self.chat: types.Chat = chat
        self.deck: Deck = Deck()
        self.field: Dict[Card, Optional[Card]] = dict()
        self.trump: c.Suits = None
        self.players: List[Player] = list()
        self.started: bool = False
        self.creator: types.User = creator
        self.open: bool = True
        self.mode: str = Config.DEFAULT_GAMEMODE  # "p"

        self.attacker_index: int = 0
        self.winner: Player | None = None
        self.is_pass: bool = False  # Atack player is PASS
        self.is_final: bool = False

        self.attack_announce_message_ids: Dict[Card, int] = {}

        self.COUNT_CARDS_IN_START: int = Config.COUNT_CARDS_IN_START
        self.MAX_PLAYERS: int = Config.MAX_PLAYERS
        self.logger = logging.getLogger(__name__)


    def start(self):
        self.deck._fill_cards()
        self.trump = self.deck.trump
        self.started = True
        self.take_cards_from_deck()


    def rotate_players(self, list: List[Player], index: int) -> List[Player]:
        return list[index:] + list[:index]
    

    @property
    def attacking_cards(self) -> List[Card]:
        """ List attacking cards """
        return list(filter(bool, self.field.keys()))
    

    @property
    def defending_cards(self) -> List[Card]:
        """ List defending cards (filter None) """
        return list(filter(bool, self.field.values()))
    

    @property
    def any_unbeaten_card(self) -> bool:
        """ exist unbeaten card """
        return any(c is None for c in self.field.values())
    

    @property
    def all_beaten_cards(self) -> bool:
        return all(c is not None for c in self.field.values())
    

    @property
    def current_player(self) -> Player:
        return self.players[self.attacker_index]    


    @property
    def opponent_player(self) -> Player:
        return self.players[(self.attacker_index + 1) % len(self.players)]
    
    
    @property
    def support_player(self) -> Player:
        return self.players[(self.attacker_index + 2) % len(self.players)]
    

    @property
    def allow_support_attack(self) -> bool:
        """Support player can throw cards if they match field values"""
        return len(self.attacking_cards) < self.COUNT_CARDS_IN_START
    
    @property
    def allow_atack(self) -> bool:
        return len(self.attacking_cards) < self.COUNT_CARDS_IN_START and \
            len(self.defending_cards)+len(self.opponent_player.cards) > len(self.attacking_cards)
    
    
    def attack(self, card: Card) -> None:
        cur, opp = self.current_player, self.opponent_player
        self.field[card] = None
        return
    

    def defend(self, attacking_card: Card, defending_card: Card) -> None:
        cur, opp = self.current_player, self.opponent_player
        self.field[attacking_card] = defending_card
        return
    

    def _clear_field(self) -> None:
        for atk_card, def_card in self.field.items():
            self.deck.dismiss(atk_card)
            self.deck.dismiss(def_card)
        self.field = dict()
        self.attack_announce_message_ids.clear()


    def take_all_field(self)-> None:
        """ Opponent take all cards from table. """
        cards = self.attacking_cards + self.defending_cards
        self.opponent_player.add_cards(cards)
        self._clear_field()
        return
    

    def take_cards_from_deck(self) -> None:
        """Розподіляє карти порівну між гравцями"""
        players = self.rotate_players(self.players, self.attacker_index)
        
        # Підраховуємо, скільки карт потрібно кожному гравцю
        total_needed = 0
        for player in players:
            lack = max(0, self.COUNT_CARDS_IN_START - len(player.cards))
            total_needed += lack
        
        # Якщо карт в колоді менше, ніж потрібно всім, розподіляємо залишок порівну
        if len(self.deck.cards) < total_needed:
            # Для 2 гравців: порівну атакуючому/захиснику, при непарній кількості +1 атакуючому
            if len(players) == 2:
                attacker, defender = players[0], players[1]

                attacker_lack = max(0, self.COUNT_CARDS_IN_START - len(attacker.cards))
                defender_lack = max(0, self.COUNT_CARDS_IN_START - len(defender.cards))

                remaining = len(self.deck.cards)
                attacker_target = min(attacker_lack, (remaining + 1) // 2)
                defender_target = min(defender_lack, remaining - attacker_target)

                for _ in range(attacker_target):
                    try:
                        attacker.add_cards([self.deck.draw()])
                    except DeckEmptyError:
                        break

                for _ in range(defender_target):
                    try:
                        defender.add_cards([self.deck.draw()])
                    except DeckEmptyError:
                        break
            else:
                cards_per_player = len(self.deck.cards) // len(players)
                for player in players:
                    n = min(cards_per_player, max(0, self.COUNT_CARDS_IN_START - len(player.cards)))
                    cards = []
                    for _ in range(n):
                        try:
                            card = self.deck.draw()
                            cards.append(card)
                        except DeckEmptyError:
                            break
                    player.add_cards(cards)
        else:
            # Нормальний розподіл
            for player in players:
                player.draw_cards_from_deck()
        return


    def turn(self, skip_def: bool = False) -> None:
        self.logger.debug("Next Player")
        self.attacker_index = (self.attacker_index + 1 + skip_def) % len(self.players)
        self.is_pass = False
        self._clear_field()
        self.take_cards_from_deck()  # every player add cards to hand
        self.current_player.turn_started = datetime.now()