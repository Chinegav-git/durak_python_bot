from aiogram import Router, types, F
from durak.filters import IsAdminFilter
from durak.db.models import ChatSetting

router = Router()

# Цей обробник спрацює на будь-який стікер у групових чатах,
# якщо користувач є глобальним адміністратором бота.
@router.message(
    F.sticker,
    F.chat.type.in_({'group', 'supergroup'}),
    IsAdminFilter(is_admin=True)  # Перевіряємо, чи є користувач адміном бота
)
async def get_sticker_id(message: types.Message):
    """
    Відповідає на стікер, надсилаючи його file_id,
    якщо в налаштуваннях чату увімкнена відповідна опція.
    Тільки для глобальних адміністраторів бота.
    """
    settings, _ = await ChatSetting.get_or_create(id=message.chat.id)

    # Перевіряємо, чи увімкнена функція в налаштуваннях чату
    if not settings.sticker_id_helper:
        return  # Якщо вимкнено, нічого не робимо

    # Якщо всі перевірки пройдено, відповідаємо ID стікера
    await message.reply(f"Sticker ID:\n`{message.sticker.file_id}`", parse_mode="Markdown")
