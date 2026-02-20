from aiogram import Router

def setup() -> Router:
    from . import (
        get_sticker_id,
        help,
        stats,
    )

    router = Router()
    for module in (
        get_sticker_id,
        help,
        stats,
    ):
        router.include_router(module.router)

    return router
