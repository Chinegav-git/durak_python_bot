from contextlib import suppress

from aiogram import F, Bot, Router, types
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pony.orm import db_session

from durak.db import ChatSetting, UserSetting
from durak.filters.is_admin import IsAdminFilter
from durak.handlers.game.start import get_lobby_message_text
from durak.logic.game_manager import GameManager
from durak.objects.errors import NoGameInChatError

router = Router()
gm = GameManager()

# Values based on instructions.md
CARD_THEMES = {
    "classic": "Classic",
    "gold_trumps": "Gold Trumps",
}

# Values based on instructions.md
GAME_MODES = {
    "text": "📝 Текст",
    "text_and_sticker": "🃏 Текст + Стікери",
    "sticker_and_button": "🕹️ Стікери + Кнопки",
}


class SettingsStates(StatesGroup):
    main = State()
    game_mode = State()
    card_theme = State()
    stats = State()


def get_main_settings_keyboard(
    cs: ChatSetting, us: UserSetting, is_admin: bool
) -> types.InlineKeyboardMarkup:
    builder = types.InlineKeyboardBuilder()

    game_mode_text = GAME_MODES.get(cs.display_mode, "невідомо")
    builder.button(
        text=f"✍️ Режим гри ({game_mode_text})", callback_data="settings_game_mode"
    )

    card_theme_text = CARD_THEMES.get(cs.card_theme, "невідомо")
    builder.button(
        text=f"🎨 Тема карт ({card_theme_text})", callback_data="settings_card_theme"
    )

    stats_status = "✅" if us.stats else "❌"
    builder.button(
        text=f"{stats_status} Збір статистики", callback_data="settings_stats"
    )

    if is_admin:
        sticker_helper_status = "✅" if cs.sticker_id_helper else "❌"
        builder.button(
            text=f"👨‍💻 Sticker ID helper ({sticker_helper_status})",
            callback_data="settings_toggle_sticker_helper",
        )
    builder.adjust(1)
    return builder.as_markup()


@router.message(Command("settings"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def settings_command_handler(message: types.Message, state: FSMContext):
    await state.clear()

    with db_session:
        cs = ChatSetting.get(id=message.chat.id)
        us = UserSetting.get(id=message.from_user.id)
        if not cs:
            cs = ChatSetting(id=message.chat.id)
        if not us:
            us = UserSetting(id=message.from_user.id)

        is_admin = await IsAdminFilter()(message)

    await message.answer(
        "⚙️ **Налаштування**",
        reply_markup=get_main_settings_keyboard(cs, us, is_admin),
    )
    await state.set_state(SettingsStates.main)


@router.callback_query(F.data == "settings_back", StateFilter(SettingsStates))
async def back_to_main_settings_handler(call: types.CallbackQuery, state: FSMContext):
    with db_session:
        cs = ChatSetting.get(id=call.message.chat.id)
        us = UserSetting.get(id=call.from_user.id)
        is_admin = await IsAdminFilter()(call)

    with suppress(TelegramBadRequest):
        await call.message.edit_text(
            "⚙️ **Налаштування**",
            reply_markup=get_main_settings_keyboard(cs, us, is_admin),
        )
    await state.set_state(SettingsStates.main)
    await call.answer()


# Game mode
@router.callback_query(F.data == "settings_game_mode", SettingsStates.main)
async def game_mode_settings_handler(call: types.CallbackQuery, state: FSMContext):
    builder = types.InlineKeyboardBuilder()
    for mode, text in GAME_MODES.items():
        builder.button(text=text, callback_data=f"set_game_mode_{mode}")
    builder.button(text="⬅️ Назад", callback_data="settings_back")
    builder.adjust(1)

    await call.message.edit_text("✍️ **Оберіть режим гри**", reply_markup=builder.as_markup())
    await state.set_state(SettingsStates.game_mode)
    await call.answer()


@router.callback_query(F.data.startswith("set_game_mode_"), SettingsStates.game_mode)
async def set_game_mode_handler(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    game_mode = call.data.removeprefix("set_game_mode_")
    with db_session:
        cs = ChatSetting.get(id=call.message.chat.id)
        cs.display_mode = game_mode

    try:
        game = await gm.get_game_from_chat(call.message.chat.id)
        if not game.started:
            await bot.edit_message_text(
                text=await get_lobby_message_text(game),
                chat_id=game.id,
                message_id=game.message_id,
                reply_markup=game.lobby_keyboard(),
            )
    except NoGameInChatError:
        pass

    await call.answer(f"Режим гри змінено на «{GAME_MODES.get(game_mode)}»")
    await back_to_main_settings_handler(call, state)


# Card theme
@router.callback_query(F.data == "settings_card_theme", SettingsStates.main)
async def card_theme_settings_handler(call: types.CallbackQuery, state: FSMContext):
    builder = types.InlineKeyboardBuilder()
    for theme, text in CARD_THEMES.items():
        builder.button(text=text, callback_data=f"set_card_theme_{theme}")
    builder.button(text="⬅️ Назад", callback_data="settings_back")
    builder.adjust(2, 1)

    await call.message.edit_text("🎨 **Оберіть тему карт**", reply_markup=builder.as_markup())
    await state.set_state(SettingsStates.card_theme)
    await call.answer()


@router.callback_query(F.data.startswith("set_card_theme_"), SettingsStates.card_theme)
async def set_card_theme_handler(call: types.CallbackQuery, state: FSMContext):
    card_theme = call.data.removeprefix("set_card_theme_")
    with db_session:
        cs = ChatSetting.get(id=call.message.chat.id)
        cs.card_theme = card_theme

    await call.answer(f"Тему карт змінено на «{CARD_THEMES.get(card_theme)}»")
    await back_to_main_settings_handler(call, state)


# Statistics
def get_stats_keyboard(us: UserSetting) -> types.InlineKeyboardMarkup:
    builder = types.InlineKeyboardBuilder()
    stats_status = "✅" if us.stats else "❌"
    builder.button(
        text=f"{stats_status} Збір статистики", callback_data="settings_toggle_stats"
    )
    builder.button(text="⬅️ Назад", callback_data="settings_back")
    return builder.as_markup()


def get_stats_text(us: UserSetting) -> str:
    win_percentage = (
        round((us.first_places / us.games_played) * 100) if us.games_played else 0
    )
    return (
        f"📊 **Ваша статистика**\n\n"
        f"– Зіграно ігор: **{us.games_played}**\n"
        f"– Перемоги: **{us.first_places}** ({win_percentage}%)\n"
        f"– Зроблено ходів: **{us.cards_atack}**\n"
        f"– Відбито карт: **{us.cards_beaten}**"
    )


@router.callback_query(F.data == "settings_stats", SettingsStates.main)
async def stats_settings_handler(call: types.CallbackQuery, state: FSMContext):
    with db_session:
        us = UserSetting.get(id=call.from_user.id)
    await call.message.edit_text(
        get_stats_text(us), reply_markup=get_stats_keyboard(us)
    )
    await state.set_state(SettingsStates.stats)
    await call.answer()


@router.callback_query(F.data == "settings_toggle_stats", SettingsStates.stats)
async def toggle_stats_handler(call: types.CallbackQuery):
    with db_session:
        us = UserSetting.get(id=call.from_user.id)
        us.stats = not us.stats
        new_status_text = "увімкнено" if us.stats else "вимкнено"
        await call.answer(f"Збір статистики {new_status_text}")
        with suppress(TelegramBadRequest):
            await call.message.edit_text(
                get_stats_text(us), reply_markup=get_stats_keyboard(us)
            )


# Sticker ID helper
@router.callback_query(
    F.data == "settings_toggle_sticker_helper",
    SettingsStates.main,
    IsAdminFilter(),
)
async def toggle_sticker_helper_handler(call: types.CallbackQuery, state: FSMContext):
    with db_session:
        cs = ChatSetting.get(id=call.message.chat.id)
        cs.sticker_id_helper = not cs.sticker_id_helper

    await call.answer(
        f"Sticker ID helper {'увімкнено' if cs.sticker_id_helper else 'вимкнено'}"
    )
    await back_to_main_settings_handler(call, state)
