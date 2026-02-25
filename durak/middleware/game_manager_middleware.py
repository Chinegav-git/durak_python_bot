# -*- coding: utf-8 -*-
"""
Middleware для передачі GameManager в обробники.
Middleware for passing GameManager to handlers.
"""

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable, Union

class GameManagerMiddleware(BaseMiddleware):
    """
    Middleware для автоматичного передавання GameManager в обробники.
    Automatically passes GameManager to handlers.
    """
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
    
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        # Додаємо gm до data, щоб обробники могли його отримати
        # Add gm to data so handlers can receive it
        data['gm'] = self.game_manager
        return await handler(event, data)
