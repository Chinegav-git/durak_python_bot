import os
from aiogram import types
from loader import dp

# Путь к файлу со стикерами (убедись, что путь совпадает с тем, где его ищет игра)
STICKERS_FILE = "stickers.txt"

@dp.message_handler(is_admin=True, chat_type="private", content_types=types.ContentType.STICKER)
async def get_sticker_id(message: types.Message):
    """
    Отвечает на стикер, показывает ID и СОХРАНЯЕТ его в файл для игры.
    """
    sticker_id = message.sticker.file_id
    
    # 1. Читаем текущие стикеры, чтобы не добавлять дубликаты
    existing_ids = []
    if os.path.exists(STICKERS_FILE):
        with open(STICKERS_FILE, "r") as f:
            existing_ids = [line.strip() for line in f.readlines()]

    # 2. Если такого ID еще нет в файле — добавляем
    if sticker_id not in existing_ids:
        with open(STICKERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{sticker_id}\n")
        
        status_text = "✅ **Додано до бібліотеки мемів!**"
    else:
        status_text = "⚠️ **Цей мем вже є в списку.**"

    # 3. Отвечаем админу
    await message.reply(
        f"{status_text}\n\n"
        f"Sticker ID:\n`{sticker_id}`", 
        parse_mode="Markdown"
    )