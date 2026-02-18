
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils.callback_data import CallbackData

from durak.db.models.chat_settings import ChatSetting
from loader import dp

settings_cd = CallbackData("settings", "level", "value")

async def get_main_settings_keyboard(chat_id: int, is_admin: bool):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(
        text="✍️ Режим гри",
        callback_data=settings_cd.new(level="gamemode", value="main")
    ))
    markup.add(types.InlineKeyboardButton(
        text="🎨 Тема карт",
        callback_data=settings_cd.new(level="card_theme", value="main")
    ))
    markup.add(types.InlineKeyboardButton(
        text="📊 Статистика",
        callback_data=settings_cd.new(level="stats", value="main")
    ))

    # Показуємо кнопку тільки адміністраторам
    if is_admin:
        settings, _ = await ChatSetting.get_or_create(id=chat_id)
        sticker_helper_status = "✅" if settings.sticker_id_helper else "❌"
        markup.add(types.InlineKeyboardButton(
            text=f"Sticker ID Helper: {sticker_helper_status}",
            callback_data=settings_cd.new(level="toggle_sticker_helper", value="toggle")
        ))
    return markup

@dp.message_handler(Command("settings"), chat_type=['group', 'supergroup'])
async def show_settings(message: types.Message):
    user = await message.chat.get_member(message.from_user.id)
    # Тепер команда доступна всім, але клавіатура залежить від статусу адміна
    await message.answer(
        "⚙️ **Налаштування**", 
        reply_markup=await get_main_settings_keyboard(message.chat.id, user.is_chat_admin())
    )

@dp.callback_query_handler(settings_cd.filter(level="main_menu"))
async def show_main_menu(call: types.CallbackQuery):
    user = await call.message.chat.get_member(call.from_user.id)
    # При поверненні в головне меню також генеруємо правильну клавіатуру
    await call.message.edit_text(
        "⚙️ **Налаштування**", 
        reply_markup=await get_main_settings_keyboard(call.message.chat.id, user.is_chat_admin())
    )
    await call.answer()

@dp.callback_query_handler(settings_cd.filter(level="toggle_sticker_helper"))
async def toggle_sticker_helper(call: types.CallbackQuery):
    user = await call.message.chat.get_member(call.from_user.id)
    # Ця перевірка залишається, оскільки є ключовою для безпеки
    if not user.is_chat_admin():
        return await call.answer("Ця дія доступна лише адміністраторам чату.", show_alert=True)

    settings, _ = await ChatSetting.get_or_create(id=call.message.chat.id)
    settings.sticker_id_helper = not settings.sticker_id_helper
    await settings.save()

    # Оновлюємо клавіатуру, щоб показати новий статус
    await call.message.edit_reply_markup(
        reply_markup=await get_main_settings_keyboard(call.message.chat.id, user.is_chat_admin())
    )
    await call.answer()
