from aiogram import Router

def setup() -> Router:
    from . import (
        card_theme,
        game_mode,
        settings,
    )
    from .game import setup as setup_game
    from .info import setup as setup_info

    router = Router()

    game_router = setup_game()
    info_router = setup_info()

    router.include_router(game_router)
    router.include_router(info_router)

    for module in (
        card_theme,
        game_mode,
        settings,
    ):
        router.include_router(module.router)

    return router
