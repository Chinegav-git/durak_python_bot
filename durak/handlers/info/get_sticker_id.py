# -*- coding: utf-8 -*-
"""
Обработчик для получения ID стикера.

Handler for getting a sticker's ID.
"""

from aiogram import Router, types, F
from durak.filters.is_admin import IsAdminFilter
from durak.db.models import Chat, ChatSetting

router = Router()

# Этот обработчик сработает на любой стикер в групповых чатах,
# если пользователь является глобальным администратором бота.
# This handler will trigger on any sticker in group chats
# if the user is a global bot administrator.
@router.message(
    F.sticker,
    F.chat.type.in_({'group', 'supergroup'}),
    IsAdminFilter(is_admin=True)  # Проверяем, является ли пользователь админом бота
                                  # Checking if the user is a bot admin
)
async def get_sticker_id(message: types.Message):
    """
    Отвечает на стикер, отправляя его file_id,
    если в настройках чата включена соответствующая опция.
    Только для глобальных администраторов бота.

    Replies to a sticker by sending its file_id
    if the corresponding option is enabled in the chat settings.
    Only for global bot administrators.
    """
    chat, _ = await Chat.get_or_create(id=message.chat.id)
    settings, _ = await ChatSetting.get_or_create(chat=chat)

    # Проверяем, включена ли функция в настройках чата
    # Check if the feature is enabled in the chat settings
    if not settings.sticker_id_helper:
        return  # Если выключено, ничего не делаем / If disabled, do nothing

    # Если все проверки пройдены, отвечаем ID стикера
    # If all checks pass, reply with the sticker ID
    await message.reply(f"ID стикера:\n`{message.sticker.file_id}`", parse_mode="Markdown")
