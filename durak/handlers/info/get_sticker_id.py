
from aiogram import types
from loader import dp
from durak.db.models.chat_settings import ChatSetting

@dp.message_handler(content_types=types.ContentType.STICKER, chat_type=['group', 'supergroup'])
async def get_sticker_id(message: types.Message):
    """
    Отвечает на сообщение со стикером, отправляя его file_id, 
    если в настройках чата включена соответствующая опция.
    Только для администраторов.
    """
    settings, _ = await ChatSetting.get_or_create(id=message.chat.id)
    
    # 1. Проверяем, включена ли функция в настройках чата
    if not settings.sticker_id_helper:
        return  # Если выключено, просто ничего не делаем

    # 2. Проверяем, является ли отправитель админом
    user = await message.chat.get_member(message.from_user.id)
    if not user.is_chat_admin():
        return # Если не админ, тоже ничего не делаем

    # 3. Если все проверки пройдены, отправляем ID стикера
    await message.reply(f"Sticker ID:\n`{message.sticker.file_id}`", parse_mode="Markdown")
