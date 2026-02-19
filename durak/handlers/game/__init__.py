from aiogram import Router
from aiogram.filters.callback_data import CallbackData

# Import routers from submodules
from . import (
    new, join, start, leave, global_leave, chosing, actions,
    kick, lobby_kick, close, kill, auto_leave
)

# General CallbackData for game-related actions
class GameCallback(CallbackData, prefix="game"):
    action: str
    game_id: int
    value: str = None # Optional value for moves etc.

# Master router for all game handlers
router = Router()
router.include_routers(
    new.router,
    join.router,
    start.router,
    leave.router,
    global_leave.router,
    chosing.router,
    actions.router,
    kick.router,
    lobby_kick.router, # Added lobby_kick
    close.router,
    kill.router,
    auto_leave.router
)
