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
        self.players: List[Player] = [Player(self, creator)] # <--- FIX
        self.started: bool = False
        self.creator: types.User = creator
        self.open: bool = True
        self.mode: str = Config.DEFAULT_GAMEMODE

        self.attacker_index: int = 0
        self.winner: Player | None = None
        self.durak: Player | None = None
        self.is_pass: bool = False
        self.is_final: bool = False

        self.attack_announce_message_ids: Dict[Card, int] = {}
        self.attack_sticker_message_ids: Dict[Card, int] = {}
        
        self.defender_cards_on_round_start: int = 0

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
        
        opponent = self.opponent_player
        if opponent:
            self.defender_cards_on_round_start = len(opponent.cards)

    def rotate_players(self, lst: List[Player], index: int) -> List[Player]:
        return lst[index:] + lst[:index]

    @property
    def attacking_cards(self) -> List[Card]:
        return list(filter(bool, self.field.keys()))

    @property
    def defending_cards(self) -> List[Card]:
        return list(filter(bool, self.field.values()))

    @property
    def any_unbeaten_card(self) -> bool:
        return any(c is None for c in self.field.values())

    @property
    def all_beaten_cards(self) -> bool:
        return all(c is not None for c in self.field.values())

    @property
    def current_player(self) -> Player:
        return self.players[self.attacker_index]

    @property
    def opponent_player(self) -> Optional[Player]:
        for i in range(1, len(self.players)):
            opponent_index = (self.attacker_index + i) % len(self.players)
            player = self.players[opponent_index]
            if not player.finished_game:
                return player
        return None

    @property
    def support_player(self) -> Optional[Player]:
        active_players = [p for p in self.players if not p.finished_game]
        if len(active_players) < 3:
            return None

        opponent = self.opponent_player
        if not opponent: return None

        for i in range(1, len(active_players)):
            try:
                base_index = active_players.index(opponent)
                support_index = (base_index + i) % len(active_players)
                supporter = active_players[support_index]
                if supporter != self.current_player:
                    return supporter
            except ValueError:
                return None
        return None

    @property
    def allow_support_attack(self) -> bool:
        return len(self.attacking_cards) < self.COUNT_CARDS_IN_START

    @property
    def allow_atack(self) -> bool:
        opponent = self.opponent_player
        if not opponent:
            return False
        return len(self.attacking_cards) < self.COUNT_CARDS_IN_START and \
            len(self.attacking_cards) < self.defender_cards_on_round_start

    @property
    def attacker_can_continue(self) -> bool:
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

    def take_all_field(self) -> None:
        opponent = self.opponent_player
        if not opponent:
            self._clear_field()
            return

        cards = self.attacking_cards + self.defending_cards
        opponent.add_cards(cards)
        self._clear_field()

    def take_cards_from_deck(self) -> None:
        players_in_turn = self.rotate_players(self.players, self.attacker_index)
        active_players_in_turn = [p for p in players_in_turn if not p.finished_game]

        for player in active_players_in_turn:
            player.draw_cards_from_deck()

    def turn(self, skip_def: bool = False) -> None:
        self.logger.debug(f"Switching turn. Skip defender: {skip_def}")
        
        if not skip_def:
            # On successful defense ("Бито"), the defender becomes the new attacker.
            if self.opponent_player:
                self.attacker_index = self.players.index(self.opponent_player)
            # If no opponent is found (e.g., they just won), we must find the next
            # active player to prevent the turn from stopping.
            else:
                # This logic finds the next player in order who hasn't finished.
                start_index = self.attacker_index
                # Loop through all players to find the next valid one.
                for i in range(1, len(self.players) + 1):
                    next_index = (start_index + i) % len(self.players)
                    if not self.players[next_index].finished_game:
                        self.attacker_index = next_index
                        break
                else:
                    # This could happen at the very end of the game.
                    self.logger.warning("No active player found to continue.")

        self.is_pass = False
        self._clear_field()
        self.take_cards_from_deck()
        
        opponent = self.opponent_player
        if opponent:
            self.defender_cards_on_round_start = len(opponent.cards)
        else:
            self.defender_cards_on_round_start = 0
        
        # Check if players list is not empty and current_player has not finished
        if self.players and self.attacker_index < len(self.players) and not self.current_player.finished_game:
            self.current_player.turn_started = datetime.now()
