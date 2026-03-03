# -*- coding: utf-8 -*-
"""
# RU: Middleware для автоматического определения и установки языка пользователя.
#
# Это ПО промежуточного слоя перехватывает входящие события (сообщения, 
# колбэки, инлайн-запросы), определяет язык пользователя и устанавливает
# его для текущего запроса. Это позволяет всем остальным частям системы
# использовать правильную локализацию.
#
# EN: Middleware for automatic user language detection and setup.
#
# This middleware intercepts incoming events (messages, callbacks,
# inline queries), determines the user's language, and sets it
# for the current request. This allows all other parts of the system
# to use the correct localization.
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
    """# RU: Middleware для автоматического определения и установки языка пользователя.
# EN: Middleware to automatically detect and set user language."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # RU: Извлекаем объект пользователя из разных типов событий.
        # EN: Extract the user object from different event types.
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

        # RU: Устанавливаем язык по умолчанию, чтобы избежать ошибок, если пользователь не найден.
        # EN: Set a default language to avoid errors if the user is not found.
        lang_code = "ru"

        if user:
            # RU: Получаем или определяем язык пользователя.
            # EN: Get or detect the user's language.
            lang_code = await language_manager.get_or_detect_language(user)

        # RU: Устанавливаем определенный язык для текущего запроса.
        # EN: Set the determined language for the current request.
        set_language(lang_code)

        # ИСПРАВЛЕНО: Передаем в обработчики все необходимые переменные: l и m.
        # `l` - это сам объект i18n, `m` - это менеджер языков.
        # FIXED: Pass all necessary variables to handlers: l and m.
        # `l` is the i18n object itself, `m` is the language manager.
        data['l'] = i18n
        data['m'] = language_manager
        data['user_language'] = lang_code

        # RU: Вызываем следующий обработчик в цепочке.
        # EN: Call the next handler in the chain.
        return await handler(event, data)
