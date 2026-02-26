# -*- coding: utf-8 -*-
"""
Middleware for automatic language detection and setting.
Проміжне ПЗ для автоматичного виявлення та встановлення мови.
"""

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from durak.utils.i18n import set_language
from durak.utils.language_detector import language_manager


class LanguageMiddleware(BaseMiddleware):
    """Middleware to automatically detect and set user language."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Extract user from the event
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if user:
            # Get or detect user language
            language = await language_manager.get_or_detect_language(user)
            
            # Set the language for this request
            set_language(language)
            
            # Store language in data for handlers to use
            data['user_language'] = language
        
        # Call the handler
        return await handler(event, data)
