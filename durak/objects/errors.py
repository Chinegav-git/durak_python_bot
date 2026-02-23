# -*- coding: utf-8 -*-
"""
Пользовательские исключения для игровой логики.

Этот модуль определяет классы исключений, специфичные для игры «Дурак».
Они используются для контроля за ходом игры и обработки ошибочных ситуаций,
таких как некорректные ходы, проблемы с лобби или состоянием игры.

-------------------------------------------------------------------------------------

Custom exceptions for game logic.

This module defines exception classes specific to the "Durak" game.
They are used to control the game flow and handle error situations,
such as invalid moves, lobby issues, or game state problems.
"""

class NotAllowedMove(Exception):
    """Вызывается, когда игрок пытается сделать недопустимый ход.
    Raised when a player attempts to make an invalid move.
    """
    pass


class DeckEmptyError(Exception):
    """Вызывается при попытке взять карту из пустой колоды.
    Raised when attempting to draw a card from an empty deck.
    """
    pass


class NoGameInChatError(Exception):
    """Вызывается, если в чате не найдено активной игры.
    Raised if no active game is found in the chat.
    """
    pass


class GameNotFoundError(Exception):
    """
    ДОБАВЛЕНО (стабилизация): Вызывается, если игра не найдена по какому-либо критерию (например, по ID пользователя).
    ADDED (stabilization): Raised if a game is not found by some criteria (e.g., by user ID).
    """
    pass


class AlreadyJoinedError(Exception):
    """Вызывается, когда пользователь пытается присоединиться к игре, в которой уже состоит.
    Raised when a user tries to join a game they are already in.
    """
    pass


class AlreadyJoinedInGlobalError(Exception):
    """Вызывается, когда пользователь пытается присоединиться к игре, состоя в другой игре (в другом чате).
    Raised when a user tries to join a game while already being in another game (in a different chat).
    """
    pass


class LobbyClosedError(Exception):
    """Вызывается при попытке присоединиться к закрытому лобби.
    Raised when attempting to join a closed lobby.
    """
    pass


class NotEnoughPlayersError(Exception):
    """Вызывается при попытке начать игру с недостаточным количеством игроков.
    Raised when trying to start a game with an insufficient number of players.
    """
    pass


class GameAlreadyInChatError(Exception):
    """Вызывается при попытке создать игру в чате, где она уже существует.
    Raised when trying to create a game in a chat where one already exists.
    """
    pass


class LimitPlayersInGameError(Exception):
    """Вызывается при попытке присоединиться к игре с максимальным количеством игроков.
    Raised when trying to join a game that has reached its maximum player limit.
    """
    pass


class GameStartedError(Exception):
    """Вызывается при попытке выполнить действие, которое недопустимо после начала игры (например, присоединиться).
    Raised when trying to perform an action that is not allowed after the game has started (e.g., joining).
    """
    pass

class PlayerNotFoundError(Exception):
    """Вызывается, если игрок не найден в игре.
    Raised if a player is not found in the game.
    """
    pass
