# Import necessary components from the Pony ORM library
from pony.orm import PrimaryKey, Required, db_session, Optional
# Import the database object from the current package
from .database import db


class ChatSetting(db.Entity):
    id = PrimaryKey(int, auto=False, size=64)  # Telegram Chat ID
    display_mode = Required(str, default='text')  # 'text', 'text_and_sticker', or 'sticker_and_button'
    card_theme = Required(str, default='classic') # Name of the card theme file
    is_game_active = Required(bool, default=False) # True if game is active in this chat

    @staticmethod
    @db_session
    def get_or_create(chat_id):
        chat_setting = ChatSetting.get(id=chat_id)
        if not chat_setting:
            chat_setting = ChatSetting(id=chat_id)
        return chat_setting

@db_session
def get_chat_settings(chat_id: int) -> ChatSetting:
    """
    Returns chat settings for a given chat_id.
    """
    return ChatSetting.get_or_create(chat_id)
