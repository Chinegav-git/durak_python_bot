# -*- coding: utf-8 -*-
"""
Internationalization (i18n) utilities for multilingual support.
Міжнародні (i18n) утиліти для багатомовної підтримки.
"""

import os
from typing import Dict, Any
from pathlib import Path
import json


class I18n:
    """Internationalization class for managing translations."""
    
    def __init__(self, default_language: str = "uk"):
        self.default_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.current_language = default_language
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files from the locales directory."""
        locales_dir = Path(__file__).parent.parent / "locales"
        
        for lang_file in locales_dir.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading translation file {lang_file}: {e}")
    
    def set_language(self, language: str):
        """Set the current language."""
        if language in self.translations:
            self.current_language = language
        else:
            self.current_language = self.default_language
    
    def get_language(self) -> str:
        """Get the current language."""
        return self.current_language
    
    def t(self, key: str, **kwargs) -> str:
        """
        Translate a text key.
        
        Args:
            key: Translation key (e.g., 'game.created')
            **kwargs: Variables to format into the translation
            
        Returns:
            Translated text
        """
        # Try to get translation in current language
        translation = self._get_translation(key, self.current_language)
        
        # If not found, try default language
        if translation is None and self.current_language != self.default_language:
            translation = self._get_translation(key, self.default_language)
        
        # If still not found, return the key itself
        if translation is None:
            return key
        
        # Format with provided variables
        try:
            return translation.format(**kwargs)
        except (KeyError, ValueError) as e:
            print(f"Error formatting translation '{key}': {e}")
            return translation
    
    def _get_translation(self, key: str, language: str) -> str:
        """Get translation for a specific language and key."""
        if language not in self.translations:
            return None
        
        # Support nested keys like 'game.created.success'
        keys = key.split('.')
        current = self.translations[language]
        
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return None
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages with their native names."""
        return {
            'uk': 'Українська',
            'ru': 'Русский',
            'en': 'English'
        }


# Global i18n instance
i18n = I18n()


def t(key: str, **kwargs) -> str:
    """Global translation function."""
    return i18n.t(key, **kwargs)


def set_language(language: str):
    """Global function to set language."""
    i18n.set_language(language)


def get_language() -> str:
    """Global function to get current language."""
    return i18n.get_language()
