from aiogram import Router

def setup() -> Router:
    from . import (
        actions,
        auto_leave,
        close,
        global_leave,
        join,
        kick,
        kill,
        leave,
        lobby_kick,
        new,
        start,
        test_win,
    )

    router = Router()
    for module in (
        actions,
        auto_leave,
        close,
        global_leave,
        join,
        kick,
        kill,
        leave,
        lobby_kick,
        new,
        start,
        test_win,
    ):
        router.include_router(module.router)

    return router
