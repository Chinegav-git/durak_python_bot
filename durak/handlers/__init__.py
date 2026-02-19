from aiogram import Router

# Import routers from submodules
from .info import help, get_sticker_id
from . import settings
from .game import router as game_router

# Create a master router for the 'handlers' module
router = Router()

# Include submodule routers
router.include_router(help.router)
router.include_router(get_sticker_id.router)
router.include_router(settings.router)
router.include_router(game_router)
