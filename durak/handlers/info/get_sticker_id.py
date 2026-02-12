from aiogram import types
from loader import dp

# Этот хендлер будет ловить ЛЮБОЙ стикер, отправленный боту
# Фильтр is_admin=True гарантирует, что только админ сможет использовать эту функцию
@dp.message_handler(is_admin=True, content_types=types.ContentType.STICKER)
async def get_sticker_id(message: types.Message):
    """
    Отвечает на сообщение со стикером, отправляя его file_id.
    """
    # Убираем IsAdminFilter из импортов, он больше не нужен напрямую
    await message.reply(f"Sticker ID:\n`{message.sticker.file_id}`", parse_mode="Markdown")
