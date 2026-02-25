# -*- coding: utf-8 -*-
"""
Фильтр для проверки прав администратора.
Admin rights check filter.

Этот модуль содержит фильтр для проверки, является ли пользователь глобальным
администратором бота в соответствии с конфигурацией.
This module contains a filter to check if a user is a global bot administrator
according to the configuration.
"""

from aiogram import types
from aiogram.filters import Filter
from typing import Union

from config import Config

class IsAdminFilter(Filter):
    """
    Перевіряє, чи є користувач глобальним адміном БОТА (з конфігу).
    Checks if the user is a global bot administrator (from config).
    
    Args:
        is_admin: Ожидаемое значение прав администратора
        is_admin: Expected admin rights value
    """
    def __init__(self, is_admin: bool) -> None:
        self.is_admin = is_admin

    async def __call__(self, message: Union[types.Message, types.CallbackQuery]) -> bool:
        """
        Проверяет права администратора пользователя.
        Checks user's admin rights.
        
        Args:
            message: Сообщение или callback запрос от пользователя
            message: Message or callback query from user
            
        Returns:
            True если пользователь имеет ожидаемые права администратора
            True if user has expected admin rights
        """
        user_id = message.from_user.id
        return (user_id in Config.ADMINS) == self.is_admin
