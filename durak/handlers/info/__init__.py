from aiogram import Router

# Import routers from submodules
from . import help
from . import get_sticker_id
from . import stats

# Create a main router for the 'info' section
router = Router()

# Include sub-routers
router.include_routers(
    help.router,
    get_sticker_id.router,
    stats.router
)
