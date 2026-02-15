from datetime import datetime
from aiogram import types
from typing import Any, List, Dict, Optional
import logging

from . import card as c
from .deck import Deck
from .player import Player
from .card import Card
from .errors import DeckEmptyError

from config import Config


class Game:
    """ This is Game """

    def __init__(self, chat: types.Chat, creator: types.User) -> None:
        self.id = chat.id
        self.chat: types.Chat = chat
        self.deck: Deck = Deck()
        self.field: Dict[Card, Optional[Card]] = dict()
        self.trump: c.Suits = None
        self.players: List[Player] = list()
        self.started: bool = False
        self.creator: types.User = creator
        self.open: bool = True
        self.mode: str = Config.DEFAULT_GAMEMODE

        self.attacker_index: int = 0
        self.winner: Player | None = None
        self.durak: Player | None = None
        self.is_final: bool = False

        self.attack_announce_message_ids: Dict[Card, int] = {}
        self.attack_sticker_message_ids: Dict[Card, int] = {}
        
        self._temp_passed_attackers: set[int] = set()

        self.COUNT_CARDS_IN_START: int = Config.COUNT_CARDS_IN_START
        self.MAX_PLAYERS: int = Config.MAX_PLAYERS
        self.logger = logging.getLogger(__name__)

    @property
    def game_is_over(self) -> bool:
        if not self.started:
            return False

        if not self.deck.cards:
            for player in self.players:
                if not player.cards and not player.finished_game:
                    player.finished_game = True

        active_players = [p for p in self.players if not p.finished_game]

        if len(active_players) <= 1:
            if len(self.players) == 2:
                self.winner = next((p for p in self.players if p.finished_game), None)
                self.durak = next((p for p in active_players), None)
            else:
                self.durak = active_players[0] if active_players else None
            
            if not active_players:
                self.durak = None
            
            return True
        return False

    def player_for_id(self, user_id: int) -> Optional[Player]:
        return next((p for p in self.players if p.user.id == user_id), None)

    def start(self):
        self.deck._fill_cards()
        self.trump = self.deck.trump
        self.started = True
        self.take_cards_from_deck()

    @property
    def attacking_cards(self) -> List[Card]:
        return list(filter(bool, self.field.keys()))

    @property
    def defending_cards(self) -> List[Card]:
        return list(filter(bool, self.field.values()))

    @property
    def all_beaten_cards(self) -> bool:
        # Returns True if the field is not empty and all attacking cards have a defending card.
        return bool(self.field) and all(c is not None for c in self.field.values())

    @property
    def current_player(self) -> Player:
        """ The main attacker in the current turn """
        return self.players[self.attacker_index]

    @property
    def opponent_player(self) -> Optional[Player]:
        """ The player who is defending in the current turn """
        active_players = [p for p in self.players if not p.finished_game]
        if len(active_players) < 2:
            return None
        
        current_idx_in_active = active_players.index(self.current_player)
        opponent_idx_in_active = (current_idx_in_active + 1) % len(active_players)
        return active_players[opponent_idx_in_active]
    
    @property
    def attackers(self) -> List[Player]:
        """ The list of all players who can attack in this turn """
        main_attacker = self.current_player
        defender = self.opponent_player
        if not defender:
            return [main_attacker]
        
        potential_attackers = [p for p in self.players if p != defender and not p.finished_game]
        if not self.field: # First attack of the turn
            return [main_attacker]

        attackers = {main_attacker}
        field_ranks = {c.value for c in self.attacking_cards} | {c.value for c in self.defending_cards if c}

        for player in potential_attackers:
            if player == main_attacker: continue
            if any(card.value in field_ranks for card in player.cards):
                attackers.add(player)

        return list(attackers)

    @property
    def allow_atack(self) -> bool:
        """ Checks if an attack is generally allowed (card limits) """
        opponent = self.opponent_player
        if not opponent or not opponent.cards:
            return False
        
        return len(self.attacking_cards) < self.COUNT_CARDS_IN_START and \
               len(self.attacking_cards) < len(opponent.cards)

    @property
    def attacker_can_continue(self) -> bool:
        """ Checks if the MAIN attacker has any valid card to continue the attack """
        attacker = self.current_player
        if not attacker.cards or not self.allow_atack:
            return False
        
        field_values = {c.value for c in self.attacking_cards}
        field_values.update({c.value for c in self.defending_cards if c})
        
        if not field_values:
            return True
            
        return any(card.value in field_values for card in attacker.cards)

    def attack(self, card: Card) -> None:
        self.field[card] = None
        # Any attack action resets the pass state for the attacker
        self._temp_passed_attackers.discard(self.current_player.user.id)

    def defend(self, attacking_card: Card, defending_card: Card) -> None:
        self.field[attacking_card] = defending_card

    def _clear_field(self) -> None:
        for atk_card, def_card in self.field.items():
            self.deck.dismiss(atk_card)
            if def_card:
                self.deck.dismiss(def_card)
        self.field.clear()
        self.attack_announce_message_ids.clear()
        self.attack_sticker_message_ids.clear()
        self._temp_passed_attackers.clear()

    def take_all_field(self) -> None:
        opponent = self.opponent_player
        if not opponent:
            self._clear_field()
            return

        cards = self.attacking_cards + self.defending_cards
        opponent.add_cards(cards)
        self._clear_field()

    def take_cards_from_deck(self) -> None:
        # Simplified: all active players draw up to the required count.
        # The order is less critical here than for turn switching.
        active_players = [p for p in self.players if not p.finished_game]
        for player in active_players:
            player.draw_cards_from_deck()

    def turn(self, skip_def: bool = False) -> None:
        self.logger.debug(f"Switching turn. Skip defender: {skip_def}")
        
        active_players = [p for p in self.players if not p.finished_game]
        if len(active_players) < 2:
            return

        current_attacker_active_idx = active_players.index(self.current_player)

        if not skip_def:  # Normal turn: defender becomes attacker
            next_attacker_active_idx = (current_attacker_active_idx + 1) % len(active_players)
        else:  # Defender took cards, skip them: next is after defender
            next_attacker_active_idx = (current_attacker_active_idx + 2) % len(active_players)
        
        next_attacker = active_players[next_attacker_active_idx]
        self.attacker_index = self.players.index(next_attacker)

        self._clear_field()
        self.take_cards_from_deck()
        if not self.current_player.finished_game:
            self.current_player.turn_started = datetime.now()