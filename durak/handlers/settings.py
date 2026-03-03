# -*- coding: utf-8 -*-
"""
# RU: Центральный модуль для управления настройками чата.
#
# EN: The central module for managing chat settings.
"""

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from durak.db.models import Chat, ChatSetting
from durak.logic import utils
from durak.utils.i18n import I18n
from durak.utils.language_detector import LanguageManager

from .settings_callback import SettingsCallback

router = Router()


def get_language_keyboard(
    current_language: str, l: I18n
) -> types.InlineKeyboardMarkup:
    """
    # RU: Создает и возвращает клавиатуру для выбора языка.
    # EN: Creates and returns the language selection keyboard.
    """
    builder = InlineKeyboardBuilder()
    languages = l.get_available_languages()

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

    builder.button(
        text=l.t("buttons.back"),
        callback_data=SettingsCallback(level="main_menu").pack(),
    )
    builder.adjust(1)

    return builder.as_markup()


async def get_main_settings_keyboard(
    chat: types.Chat, is_admin: bool, user_id: int, l: I18n, lang_m: LanguageManager
) -> types.InlineKeyboardMarkup:
    """
    # RU: Генерирует и возвращает главное меню настроек.
    # EN: Generates and returns the main settings menu.
    """
    builder = InlineKeyboardBuilder()

    if user_id:
        current_lang = await lang_m.get_user_language(user_id)
        lang_names = {"uk": "UA", "ru": "RU", "en": "EN"}
        current_lang_name = lang_names.get(current_lang, current_lang.upper())
        builder.button(
            text=f"🌐 Мова ({current_lang_name})",
            callback_data=SettingsCallback(level="language").pack(),
        )

    builder.button(
        text=l.t("buttons.game_mode"),
        callback_data=SettingsCallback(level="gamemode").pack(),
    )

    builder.button(
        text=l.t("buttons.card_theme"),
        callback_data=SettingsCallback(level="card_theme").pack(),
    )

    if is_admin:
        db_chat, _ = await Chat.get_or_create(
            id=chat.id, defaults={"title": chat.title or "Unknown", "type": chat.type}
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
async def settings_command_handler(message: types.Message, l: I18n, lang_m: LanguageManager):
    """
    # RU: Обработчик команды /settings.
    # EN: Handler for the /settings command.
    """
    is_admin = await utils.user_can_change_settings(
        message.bot, message.from_user.id, message.chat.id
    )
    await message.answer(
        l.t("settings.title"),
        reply_markup=await get_main_settings_keyboard(
            message.chat, is_admin, message.from_user.id, l, lang_m
        ),
    )


@router.callback_query(SettingsCallback.filter(F.level == "main_menu"))
async def back_to_main_settings_handler(call: types.CallbackQuery, l: I18n, lang_m: LanguageManager):
    """
    # RU: Обработчик для кнопки "Назад" в главное меню.
    # EN: Handler for the "Back" button to the main menu.
    """
    is_admin = await utils.user_can_change_settings(
        call.bot, call.from_user.id, call.message.chat.id
    )
    await call.message.edit_text(
        l.t("settings.title"),
        reply_markup=await get_main_settings_keyboard(
            call.message.chat, is_admin, call.from_user.id, l, lang_m
        ),
    )
    await call.answer()


@router.callback_query(SettingsCallback.filter(F.level == "toggle_sticker_helper"))
async def toggle_sticker_helper_handler(call: types.CallbackQuery, l: I18n, lang_m: LanguageManager):
    """
    # RU: Обработчик для переключения помощника ID стикеров.
    # EN: Handler for toggling the sticker ID helper.
    """
    if not await utils.user_can_change_settings(
        call.bot, call.from_user.id, call.message.chat.id
    ):
        await call.answer(l.t("errors.not_enough_rights"), show_alert=True)
        return

    chat = call.message.chat
    db_chat, _ = await Chat.get_or_create(
        id=chat.id, defaults={"title": chat.title or "Unknown", "type": chat.type}
    )
    cs, _ = await ChatSetting.get_or_create(chat=db_chat)
    cs.sticker_id_helper = not cs.sticker_id_helper
    await cs.save()

    new_status = l.t("settings.sticker_helper_on") if cs.sticker_id_helper else l.t("settings.sticker_helper_off")
    await call.answer(l.t("settings.sticker_helper_changed", status=new_status))

    is_admin = await utils.user_can_change_settings(
        call.bot, call.from_user.id, call.message.chat.id
    )
    await call.message.edit_reply_markup(
        reply_markup=await get_main_settings_keyboard(
            chat, is_admin, call.from_user.id, l, lang_m
        )
    )


@router.callback_query(SettingsCallback.filter(F.level == "language"))
async def language_settings_handler(call: types.CallbackQuery, l: I18n, lang_m: LanguageManager):
    """
    # RU: Обработчик, который отображает меню выбора языка.
    # EN: Handler that displays the language selection menu.
    """
    current_language = await lang_m.get_user_language(call.from_user.id)
    await call.message.edit_text(
        l.t("settings.language_menu_title"),
        reply_markup=get_language_keyboard(current_language, l),
    )
    await call.answer()


@router.callback_query(SettingsCallback.filter(F.level == "set_language"))
async def set_language_handler(
    call: types.CallbackQuery, callback_data: SettingsCallback, l: I18n, lang_m: LanguageManager
):
    """
    # RU: Обработчик, который устанавливает выбранный язык.
    # EN: Handler that sets the selected language.
    """
    new_lang_code = callback_data.value
    current_language = await lang_m.get_user_language(call.from_user.id)

    # ИСПРАВЛЕНО: Предотвращаем ошибку "message is not modified",
    # выполняя действие только при реальном изменении языка.
    # FIXED: We prevent the "message is not modified" error by
    # performing the action only when the language actually changes.
    if new_lang_code != current_language:
        await lang_m.set_user_language(call.from_user.id, new_lang_code)
        l.set_language(new_lang_code)
        await call.answer(l.t("language_changed"), show_alert=True)
        
        # Перерисовываем клавиатуру, чтобы показать новую активную кнопку
        # Redraw the keyboard to show the new active button
        await call.message.edit_reply_markup(
            reply_markup=get_language_keyboard(new_lang_code, l)
        )
    else:
        # Если язык тот же, просто отвечаем на колбэк
        # If the language is the same, just answer the callback
        await call.answer()
