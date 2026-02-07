from aiogram import types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from loader import bot, dp, gm, Config, Commands
from durak.objects import *
from uuid import uuid4


@dp.inline_handler(func=lambda query: query.query == 'join_game')
async def join_inline_handler(query: types.InlineQuery):
    """ Inline handler for joining game """
    user = types.User.get_current()
    
    # Get chat from query (this is tricky - inline queries don't have direct chat info)
    # We'll need to store this information differently or use a different approach
    
    result = []
    
    # Join button
    result.append(
        InlineQueryResultArticle(
            id=f"join_{uuid4()}",
            title="👋 Приєднатися до гри",
            description="Натисніть щоб приєднатися до поточної гри",
            input_message_content=InputTextMessageContent(
                "👋 Намагаюся приєднатися до гри..."
            )
        )
    )
    
    # Start game button (only for creators/admins)
    result.append(
        InlineQueryResultArticle(
            id=f"start_{uuid4()}",
            title="🚀 Почати гру",
            description="Запустити гру (тільки для творця/адміна)",
            input_message_content=InputTextMessageContent(
                "🚀 Намагаюся запустити гру..."
            )
        )
    )
    
    await query.answer(result, cache_time=0)


@dp.chosen_inline_handler()
async def join_chosen_handler(query: types.ChosenInlineResult):
    """ Handle chosen inline result for join/start """
    user = types.User.get_current()
    
    if not query.inline_message_id:
        # This was sent to a chat, not as a reply
        return
    
    result_id = query.result_id
    
    if result_id.startswith('join_'):
        # Handle join
        # We need to find which game this belongs to
        # This is complex with inline mode, so we'll need to track this differently
        await bot.edit_message_text(
            inline_message_id=query.inline_message_id,
            text=f"🔄 {user.get_mention(as_html=True)} приєднується до гри..."
        )
        # Note: In a real implementation, you'd need to track which chat this belongs to
        # For now, this shows the concept
        
    elif result_id.startswith('start_'):
        # Handle start game
        await bot.edit_message_text(
            inline_message_id=query.inline_message_id,
            text=f"🚀 {user.get_mention(as_html=True)} запускає гру..."
        )
        # Note: Same issue with chat tracking
