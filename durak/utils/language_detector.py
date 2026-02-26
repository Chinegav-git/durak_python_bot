# -*- coding: utf-8 -*-
"""
Language detection and user preference management.
Виявлення мови та управління мовними налаштуваннями користувачів.
"""

import asyncio
from typing import Optional
from aiogram.types import User, Chat

from durak.db.tortoise_config import get_db_session
from durak.db.models import UserSetting


class LanguageManager:
    """Manages user language preferences."""
    
    @staticmethod
    async def get_user_language(user_id: int) -> str:
        """
        Get user's preferred language.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Language code (uk, ru, en)
        """
        try:
            async with get_db_session():
                # First get the User, then UserSetting
                from durak.db.models import User
                user = await User.get_or_none(id=user_id)
                if user:
                    setting = await UserSetting.get_or_none(user=user)
                    if setting and setting.language:
                        return setting.language
        except Exception as e:
            print(f"Error getting user language preference: {e}")
        
        # Detect language from user's language code if available
        return "uk"  # Default to Ukrainian
    
    @staticmethod
    async def set_user_language(user_id: int, language: str) -> bool:
        """
        Set user's preferred language.
        
        Args:
            user_id: Telegram user ID
            language: Language code (uk, ru, en)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with get_db_session():
                from durak.db.models import User
                user = await User.get_or_none(id=user_id)
                if user:
                    setting, created = await UserSetting.get_or_create(
                        user=user,
                        defaults={'language': language}
                    )
                    if not created:
                        setting.language = language
                        await setting.save()
                    return True
        except Exception as e:
            print(f"Error setting user language preference: {e}")
            return False
    
    @staticmethod
    async def detect_language_from_user(user: User) -> str:
        """
        Detect language from user's Telegram profile.
        
        Args:
            user: Telegram user object
            
        Returns:
            Detected language code
        """
        if not user.language_code:
            return "uk"  # Default to Ukrainian
        
        lang_code = user.language_code.lower()
        
        # Map language codes to our supported languages
        if lang_code.startswith('uk'):
            return 'uk'
        elif lang_code.startswith('ru'):
            return 'ru'
        elif lang_code.startswith('en'):
            return 'en'
        else:
            return 'uk'  # Default to Ukrainian for other languages
    
    @staticmethod
    async def get_or_detect_language(user: User) -> str:
        """
        Get user's preferred language or detect from profile.
        
        Args:
            user: Telegram user object
            
        Returns:
            Language code
        """
        # First try to get saved preference
        saved_lang = await LanguageManager.get_user_language(user.id)
        if saved_lang:
            return saved_lang
        
        # Detect from user profile and save
        detected_lang = LanguageManager.detect_language_from_user(user)
        await LanguageManager.set_user_language(user.id, detected_lang)
        
        return detected_lang


# Global language manager instance
language_manager = LanguageManager()
