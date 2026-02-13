from pony.orm import PrimaryKey, Required, Optional
from .database import db


class ChatSetting(db.Entity):
    id = PrimaryKey(int, auto=False, size=64)  # Telegram Chat ID
    display_mode = Required(str, default='text')  # 'text', 'text_and_sticker', or 'sticker_and_button'
    is_game_active = Required(bool, default=False) # True if game is active in this chat

    @staticmethod
    def get_or_create(chat_id):
        chat_setting = ChatSetting.get(id=chat_id)
        if not chat_setting:
            chat_setting = ChatSetting(id=chat_id)
        return chat_setting
