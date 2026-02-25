# -*- coding: utf-8 -*-
"""
Менеджер для обробки callback запитів з запобіганням накопичення.
Manager for handling callback requests with accumulation prevention.
"""

import asyncio
from typing import Dict, Set, Optional
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
import logging

logger = logging.getLogger(__name__)

class CallbackManager:
    """
    Менеджер для контролю callback запитів.
    Controls callback requests.
    """
    
    def __init__(self):
        # Активні callback'и, що очікують обробки
        # Active callbacks waiting for processing
        self.pending_callbacks: Set[str] = set()
        
        # Час очікування для callback (секунди)
        # Callback timeout (seconds)
        self.callback_timeout = 30
        
        # Максимальна кількість одночасних callback'ів
        # Maximum simultaneous callbacks
        self.max_concurrent_callbacks = 10
        
        # Лог оброблених callback'ів для запобігання дублюванню
        # Processed callbacks log to prevent duplication
        self.processed_callbacks: Dict[str, float] = {}
        
    async def process_callback(self, callback: CallbackQuery, handler_func) -> bool:
        """
        Безпечна обробка callback з перевіркою дублікатів та таймаутів.
        Safe callback processing with duplicate and timeout checks.
        """
        callback_id = f"{callback.from_user.id}_{callback.message.message_id}_{callback.data}"
        
        # Перевіряємо, чи не обробляли цей callback раніше
        # Check if this callback was processed before
        if callback_id in self.processed_callbacks:
            logger.warning(f"Duplicate callback detected: {callback_id}")
            await self._answer_callback(callback, "Ця дія вже оброблена", show_alert=True)
            return False
        
        # Перевіряємо, чи не забагато одночасних callback'ів
        # Check if too many concurrent callbacks
        if len(self.pending_callbacks) >= self.max_concurrent_callbacks:
            logger.warning(f"Too many concurrent callbacks: {len(self.pending_callbacks)}")
            await self._answer_callback(callback, "Занадто багато запитів, спробуйте пізніше", show_alert=True)
            return False
        
        # Додаємо до списку очікуючих
        # Add to pending list
        self.pending_callbacks.add(callback_id)
        
        try:
            # Встановлюємо відповідь на callback для запобігання таймауту
            # Set callback answer to prevent timeout
            await callback.answer("Обробка...")
            
            # Обробляємо callback з таймаутом
            # Process callback with timeout
            await asyncio.wait_for(handler_func(), timeout=self.callback_timeout)
            
            # Позначаємо як оброблений
            # Mark as processed
            self.processed_callbacks[callback_id] = asyncio.get_event_loop().time()
            
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"Callback timeout: {callback_id}")
            await self._answer_callback(callback, "Час очікування вичерпано", show_alert=True)
            return False
            
        except Exception as e:
            logger.error(f"Callback processing error: {callback_id}, error: {e}")
            await self._answer_callback(callback, "Помилка обробки", show_alert=True)
            return False
            
        finally:
            # Видаляємо зі списку очікуючих
            # Remove from pending list
            self.pending_callbacks.discard(callback_id)
    
    async def _answer_callback(self, callback: CallbackQuery, text: str, show_alert: bool = False):
        """
        Безпечна відповідь на callback з обробкою помилок.
        Safe callback answer with error handling.
        """
        try:
            await callback.answer(text, show_alert=show_alert)
        except TelegramBadRequest as e:
            if "query is too old" in str(e):
                logger.warning(f"Callback too old: {callback.id}")
            else:
                logger.error(f"Callback answer error: {e}")
        except Exception as e:
            logger.error(f"Unexpected callback answer error: {e}")
    
    def cleanup_old_callbacks(self):
        """
        Очищення старих записів про оброблені callback'и.
        Cleanup old processed callback records.
        """
        current_time = asyncio.get_event_loop().time()
        old_threshold = current_time - 300  # 5 хвилин
        
        old_callbacks = [
            callback_id for callback_id, timestamp in self.processed_callbacks.items()
            if timestamp < old_threshold
        ]
        
        for callback_id in old_callbacks:
            del self.processed_callbacks[callback_id]
        
        if old_callbacks:
            logger.info(f"Cleaned up {len(old_callbacks)} old callbacks")

# Глобальний екземпляр менеджера
# Global manager instance
callback_manager = CallbackManager()
