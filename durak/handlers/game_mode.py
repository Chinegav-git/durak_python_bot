# -*- coding: utf-8 -*-
"""
Обработчики для настройки режима игры.
Позволяет пользователю выбирать, как будет отображаться игровой процесс в чате.
Handlers for configuring the game mode.
Allows the user to choose how the gameplay will be displayed in the chat.
"""

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from durak.db.models import Chat, ChatSetting
from .settings_callback import SettingsCallback # ИСПРАВЛЕНО: Прямой импорт

router = Router()

async def get_gamemode_keyboard(chat: types.Chat):
    """
    Генерирует клавиатуру для настроек режима игры.
    Отмечает текущий выбранный режим.
    
    ИСПРАВЛЕНО:
    - Сигнатура функции теперь принимает объект `chat` вместо `chat_id`.
    - Добавлены `defaults` при вызове `Chat.get_or_create` для предотвращения `ValidationError`.

    Generates the keyboard for game mode settings.
    Marks the currently selected mode.
    
    FIXED:
    - Function signature now accepts `chat` object instead of `chat_id`.
    - Added `defaults` in `Chat.get_or_create` call to prevent `ValidationError`.
    """
    db_chat, _ = await Chat.get_or_create(
        id=chat.id, 
        defaults={'title': chat.title or "Unknown", 'type': chat.type}
    )
    cs, _ = await ChatSetting.get_or_create(chat=db_chat)
    current_mode = cs.game_mode

    # Словарь доступных режимов игры
    # Dictionary of available game modes
    # ИСПРАВЛЕНО: Текст кнопок приведен к единому русскому языку.
    # FIXED: Button text has been unified to a single Russian language.
    modes = {
        "text": "📝 Текст",
        "text_and_sticker": "🃏 Текст + Стикеры",
        "sticker_and_button": "🕹️ Стикеры + Кнопки"
    }

    builder = InlineKeyboardBuilder()

    # Добавление кнопок для каждого режима
    # Add buttons for each mode
    for mode_id, mode_name in modes.items():
        text = f"» {mode_name} «" if current_mode == mode_id else mode_name
        builder.button(
            text=text,
            # ИСПРАВЛЕНО: Добавлен .pack() для корректной сериализации данных
            # FIXED: Added .pack() for correct data serialization
            callback_data=SettingsCallback(level="gamemode_select", value=mode_id).pack()
        )
    
    # Кнопка "Назад" для возврата в главное меню настроек
    # "Back" button to return to the main settings menu
    builder.row(types.InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data=SettingsCallback(level="main_menu").pack()
    ))
    builder.adjust(1)
    return builder.as_markup()


@router.message(Command("gamemode"))
async def set_game_mode(message: types.Message):
    """
    Обработчик команды /gamemode.
    Сообщает пользователю текущий режим и предлагает использовать /settings для изменения.
    
    ИСПРАВЛЕНО:
    - Добавлены `defaults` при вызове `Chat.get_or_create` для предотвращения `ValidationError`.

    Handler for the /gamemode command.
    Informs the user about the current mode and suggests using /settings to change it.
    
    FIXED:
    - Added `defaults` in `Chat.get_or_create` call to prevent `ValidationError`.
    """
    db_chat, _ = await Chat.get_or_create(
        id=message.chat.id, 
        defaults={'title': message.chat.title or "Unknown", 'type': message.chat.type}
    )
    chat_setting, _ = await ChatSetting.get_or_create(chat=db_chat)
    current_mode = chat_setting.game_mode

    await message.answer(
        f"Текущий режим игры: `{current_mode}`.\n\n"
        f"Чтобы изменить режим, воспользуйтесь меню /settings.",
        parse_mode='Markdown'
    )


@router.callback_query(SettingsCallback.filter(F.level == "gamemode"))
async def show_gamemode_settings(call: types.CallbackQuery):
    """
    Показывает меню выбора режима игры по нажатию на кнопку в настройках.
    Shows the game mode selection menu when the button in settings is pressed.
    """
    await call.message.edit_text(
        "✍️ <b>Режим игры</b>\n\nВыберите, как будут отображаться карты и игровой процесс:",
        reply_markup=await get_gamemode_keyboard(call.message.chat)
    )
    await call.answer()


@router.callback_query(SettingsCallback.filter(F.level == "gamemode_select"))
async def set_gamemode_callback(call: types.CallbackQuery, callback_data: SettingsCallback):
    """
    Устанавливает выбранный режим игры из callback'а.
    Обновляет запись в БД и изменяет клавиатуру, чтобы отразить выбор.
    
    ИСПРАВЛЕНО:
    - Добавлены `defaults` при вызове `Chat.get_or_create` для предотвращения `ValidationError`.
    - Вызов `get_gamemode_keyboard` теперь передает объект `chat`.

    Sets the chosen game mode from a callback.
    Updates the DB record and modifies the keyboard to reflect the choice.
    
    FIXED:
    - Added `defaults` in `Chat.get_or_create` call to prevent `ValidationError`.
    - `get_gamemode_keyboard` call now passes `chat` object.
    """
    new_mode = callback_data.value
    chat = call.message.chat

    db_chat, _ = await Chat.get_or_create(
        id=chat.id,
        defaults={'title': chat.title or "Unknown", 'type': chat.type}
    )
    chat_setting, _ = await ChatSetting.get_or_create(chat=db_chat)
    if chat_setting.game_mode != new_mode:
        chat_setting.game_mode = new_mode
        await chat_setting.save()
        await call.answer("✅ Режим игры изменен")
        
        # Обновление клавиатуры для отображения нового выбора
        # Update the keyboard to show the new selection
        await call.message.edit_reply_markup(
            reply_markup=await get_gamemode_keyboard(chat)
        )
    else:
        await call.answer("Этот режим уже установлен")