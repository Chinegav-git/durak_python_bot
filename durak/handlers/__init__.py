from aiogram import Router

# Импортируем агрегированные роутеры из под-пакетов
from .info import router as info_router
from .game import router as game_router
from .settings import router as settings_router
from .stats import router as stats_router
from .card_theme import router as card_theme_router
from .game_mode import router as game_mode_router

# Создаем главный роутер для всех обработчиков
main_router = Router()

# Включаем в него роутеры всех разделов
main_router.include_routers(
    info_router,
    game_router,
    settings_router,
    stats_router,
    card_theme_router,
    game_mode_router
)
