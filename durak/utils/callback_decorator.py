# -*- coding: utf-8 -*-
"""
Декоратор для безпечної обробки callback'ів.
Decorator for safe callback handling.
"""

import functools
from typing import Callable, Any
from aiogram.types import CallbackQuery
from .callback_manager import callback_manager

def safe_callback_handler(show_error: bool = True, timeout: int = 30):
    """
    Декоратор для безпечної обробки callback'ів.
    Decorator for safe callback handling.
    
    Args:
        show_error: Показувати помилки користувачу
        timeout: Таймаут обробки
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(callback: CallbackQuery, *args, **kwargs) -> Any:
            # Створюємо обгортку для обробки
            async def handler():
                return await func(callback, *args, **kwargs)
            
            # Використовуємо менеджер для безпечної обробки
            success = await callback_manager.process_callback(callback, handler)
            
            if not success:
                # Якщо обробка не вдалася, просто виходимо
                return None
                
            return await func(callback, *args, **kwargs)
        
        return wrapper
    return decorator

# Простий декоратор для автоматичної відповіді на callback
def auto_callback_answer(text: str = "✅", show_alert: bool = False):
    """
    Декоратор для автоматичної відповіді на callback.
    Decorator for automatic callback answer.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(callback: CallbackQuery, *args, **kwargs) -> Any:
            try:
                result = await func(callback, *args, **kwargs)
                # Відповідаємо на callback, якщо функція не зробила цього
                try:
                    await callback.answer(text, show_alert=show_alert)
                except:
                    pass  # Ігноруємо помилку, якщо callback вже оброблено
                return result
            except Exception as e:
                # Відповідаємо про помилку
                try:
                    await callback.answer("❌ Помилка", show_alert=True)
                except:
                    pass
                raise e
        
        return wrapper
    return decorator
