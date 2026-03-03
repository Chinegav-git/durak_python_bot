# -*- coding: utf-8 -*-
"""
# RU: Middleware для автоматического определения и установки языка пользователя.
#
# EN: Middleware for automatic user language detection and setup.
"""

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, InlineQuery

from durak.utils import i18n
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
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        elif isinstance(event, InlineQuery):
            user = event.from_user

        lang_code = "ru"  # Язык по умолчанию

        if user:
            lang_code = await language_manager.get_or_detect_language(user)

        i18n.set_language(lang_code)

        data['l'] = i18n.i18n
        # ИСПРАВЛЕНО: Ключ изменен на 'lang_m', чтобы избежать конфликта с ChatSetting Middleware.
        # FIXED: Key changed to 'lang_m' to avoid conflict with ChatSetting Middleware.
        data['lang_m'] = language_manager
        data['user_language'] = lang_code

        return await handler(event, data)
