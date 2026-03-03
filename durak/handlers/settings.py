# -*- coding: utf-8 -*-
"""
# RU: Центральный модуль для управления настройками чата.
#
# Этот модуль отвечает за:
# - Обработку команды /settings.
# - Отображение главного меню настроек.
# - Навигацию по разделам: выбор языка, режим игры, тема карт.
# - Обработку изменения настроек, таких как включение/выключение
#   вспомогательных инструментов для администраторов.
#
# EN: The central module for managing chat settings.
#
# This module is responsible for:
# - Handling the /settings command.
# - Displaying the main settings menu.
# - Navigation through sections: language selection, game mode, card theme.
# - Handling changes to settings, such as enabling/disabling
#   helper tools for administrators.
"""

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from durak.db.models import Chat, ChatSetting
from durak.logic import utils
# ИСПРАВЛЕНО: Добавлен импорт i18n для работы с языками.
# FIXED: Added i18n import for language operations.
from durak.utils.i18n import t, set_language, i18n
from durak.utils.language_detector import language_manager
# ИСПРАВЛЕНО: Теперь используется SettingsCallback для навигации по меню.
# FIXED: Now using SettingsCallback for menu navigation.
from .settings_callback import SettingsCallback

router = Router()


def get_language_keyboard(current_language: str) -> types.InlineKeyboardMarkup:
    """
    # RU: Создает и возвращает клавиатуру для выбора языка.
    # EN: Creates and returns the language selection keyboard.
    """
    builder = InlineKeyboardBuilder()

    languages = i18n.get_available_languages()

    for lang_code, lang_name in languages.items():
        is_current = lang_code == current_language
        text = f"🌐 {lang_name} {'✅' if is_current else ''}"
        builder.button(
            text=text,
            callback_data=SettingsCallback(
                level="set_language", value=lang_code
            ).pack(),
        )

    builder.adjust(1)

    # RU: Кнопка "Назад"
    # EN: Back button
    builder.button(
        text=t("buttons.back"),
        callback_data=SettingsCallback(level="main_menu").pack(),
    )
    builder.adjust(1)

    return builder.as_markup()


async def get_main_settings_keyboard(
    chat: types.Chat, is_admin: bool, user_id: int = None
) -> types.InlineKeyboardMarkup:
    """
    # RU: Генерирует и возвращает главное меню настроек в виде inline-клавиатуры.
    # EN: Generates and returns the main settings menu as an inline keyboard.
    """
    builder = InlineKeyboardBuilder()

    # RU: Кнопка для выбора языка. Показывает текущий язык пользователя.
    # EN: Button for language selection. Shows the user's current language.
    if user_id:
        current_lang = await language_manager.get_user_language(user_id)
        lang_names = {"uk": "UA", "ru": "RU", "en": "EN"}
        current_lang_name = lang_names.get(current_lang, current_lang.upper())
        builder.button(
            text=f"🌐 Мова ({current_lang_name})",
            callback_data=SettingsCallback(level="language").pack(),
        )

    # RU: Кнопка для перехода в меню выбора режима игры.
    # EN: Button to navigate to the game mode selection menu.
    builder.button(
        text=t("buttons.game_mode"),
        callback_data=SettingsCallback(level="gamemode").pack(),
    )

    # RU: Кнопка для перехода в меню выбора темы карт.
    # EN: Button to navigate to the card theme selection menu.
    builder.button(
        text=t("buttons.card_theme"),
        callback_data=SettingsCallback(level="card_theme").pack(),
    )

    # RU: Администраторская опция для включения/выключения помощника по ID стикеров.
    # EN: Administrator option to enable/disable the sticker ID helper.
    if is_admin:
        db_chat, _ = await Chat.get_or_create(
            id=chat.id,
            defaults={"title": chat.title or "Unknown", "type": chat.type},
        )
        cs, _ = await ChatSetting.get_or_create(chat=db_chat)
        sticker_helper_status = "✅" if cs.sticker_id_helper else "❌"

        builder.button(
            text=f"👨‍💻 Помічник ID стикерів ({sticker_helper_status})",
            callback_data=SettingsCallback(level="toggle_sticker_helper").pack(),
        )

    builder.adjust(1)
    return builder.as_markup()


@router.message(Command("settings"))
async def settings_command_handler(message: types.Message):
    """
    # RU: Обработчик команды /settings.
    # Проверяет права пользователя и отображает главное меню настроек.
    # EN: Handler for the /settings command.
    # Checks user permissions and displays the main settings menu.
    """
    is_admin = await utils.user_can_change_settings(
        message.bot, message.from_user.id, message.chat.id
    )
    await message.answer(
        t("settings.title"),
        reply_markup=await get_main_settings_keyboard(
            message.chat, is_admin, message.from_user.id
        ),
    )


@router.callback_query(SettingsCallback.filter(F.level == "main_menu"))
async def back_to_main_settings_handler(call: types.CallbackQuery):
    """
    # RU: Обработчик для кнопки "Назад", который возвращает пользователя в главное меню настроек.
    # EN: Handler for the "Back" button, which returns the user to the main settings menu.
    """
    is_admin = await utils.user_can_change_settings(
        call.bot, call.from_user.id, call.message.chat.id
    )
    await call.message.edit_text(
        t("settings.title"),
        reply_markup=await get_main_settings_keyboard(
            call.message.chat, is_admin, call.from_user.id
        ),
    )
    await call.answer()


@router.callback_query(SettingsCallback.filter(F.level == "toggle_sticker_helper"))
async def toggle_sticker_helper_handler(call: types.CallbackQuery):
    """
    # RU: Обработчик для переключения помощника ID стикеров.
    # Доступно только администраторам.
    # EN: Handler for toggling the sticker ID helper.
    # Available only to administrators.
    """
    if not await utils.user_can_change_settings(
        call.bot, call.from_user.id, call.message.chat.id
    ):
        await call.answer(t("errors.not_enough_rights"), show_alert=True)
        return

    chat = call.message.chat

    # RU: Получаем или создаем запись настроек для чата.
    # EN: Get or create the settings entry for the chat.
    db_chat, _ = await Chat.get_or_create(
        id=chat.id,
        defaults={"title": chat.title or "Unknown", "type": chat.type},
    )
    cs, _ = await ChatSetting.get_or_create(chat=db_chat)
    cs.sticker_id_helper = not cs.sticker_id_helper
    await cs.save()

    new_status = "включен" if cs.sticker_id_helper else "выключен"

    await call.answer(f"Помощник ID стикеров {new_status}")

    # RU: Обновляем клавиатуру, чтобы отразить новое состояние.
    # EN: Update the keyboard to reflect the new state.
    await call.message.edit_reply_markup(
        reply_markup=await get_main_settings_keyboard(chat, True, call.from_user.id)
    )


@router.callback_query(SettingsCallback.filter(F.level == "language"))
async def language_settings_handler(call: types.CallbackQuery):
    """
    # RU: Обработчик, который отображает меню выбора языка.
    # EN: Handler that displays the language selection menu.
    """
    current_language = await language_manager.get_user_language(call.from_user.id)

    await call.message.edit_text(
        "🌐 **Мова / Language**\n\n"
        "Оберіть мову інтерфейсу:\n"
        "Choose your interface language:",
        reply_markup=get_language_keyboard(current_language),
    )
    await call.answer()


@router.callback_query(SettingsCallback.filter(F.level == "set_language"))
async def set_language_handler(
    call: types.CallbackQuery, callback_data: SettingsCallback
):
    """
    # RU: Обработчик, который устанавливает выбранный язык.
    # Обновляет язык в БД для пользователя и в рантайме для i18n.
    # EN: Handler that sets the selected language.
    # Updates the language in the DB for the user and in runtime for i18n.
    """
    lang_code = callback_data.value

    # RU: Сохраняем выбор языка пользователя в базе данных.
    # EN: Save the user's language choice in the database.
    await language_manager.set_user_language(call.from_user.id, lang_code)

    # ИСПРАВЛЕНО: Устанавливаем язык для текущего контекста i18n.
    # Это ключевой шаг для немедленного обновления интерфейса.
    # FIXED: Set the language for the current i18n context.
    # This is a key step for immediate interface updates.
    set_language(lang_code)

    # RU: Перерисовываем меню выбора языка, чтобы показать новый выбранный язык.
    # EN: Redraw the language selection menu to show the new selected language.
    await call.message.edit_text(
        "🌐 **Мова / Language**\n\n"
        "Оберіть мову інтерфейсу:\n"
        "Choose your interface language:",
        reply_markup=get_language_keyboard(lang_code),
    )

    # ИСПРАВЛЕНО: Используем ключ локализации для ответа.
    # FIXED: Use a localization key for the answer.
    await call.answer(t("language_changed"))
