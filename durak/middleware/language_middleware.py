# -*- coding: utf-8 -*-
"""
Middleware for automatic language detection and setting.
Проміжне ПЗ для автоматичного виявлення та встановлення мови.
"""

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
# ИСПРАВЛЕНО: Добавлен импорт `InlineQuery` для корректной обработки этого типа события.
# FIXED: Added `InlineQuery` import to correctly handle this event type.
from aiogram.types import TelegramObject, Message, CallbackQuery, InlineQuery

# ИСПРАВЛЕНО: Импортируем сам объект i18n, чтобы передавать его в обработчики.
# FIXED: Import the i18n object itself to pass it to handlers.
from durak.utils import i18n
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
        # ИСПРАВЛЕНО: Добавлена ветка для `InlineQuery`.
        # Теперь middleware корректно извлекает пользователя из инлайн-запросов.
        # FIXED: Added branch for `InlineQuery`.
        # The middleware now correctly extracts the user from inline queries.
        elif isinstance(event, InlineQuery):
            user = event.from_user

        # По умолчанию устанавливаем язык, чтобы избежать ошибок, если user не найден
        # Set a default language to avoid errors if the user is not found
        lang_code = "ru" 

        if user:
            # Get or detect user language
            lang_code = await language_manager.get_or_detect_language(user)
        
        # Set the language for this request
        set_language(lang_code)
        
        # ИСПРАВЛЕНО: Передаем в обработчики все необходимые переменные: l и m.
        # `l` - это сам объект i18n, `m` - это менеджер языков.
        # FIXED: Pass all necessary variables to handlers: l and m.
        # `l` is the i18n object itself, `m` is the language manager.
        data['l'] = i18n
        data['m'] = language_manager
        data['user_language'] = lang_code
        
        # Call the handler
        return await handler(event, data)
