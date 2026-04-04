from pony.orm import Required, Set, Optional, LongStr
from .database import db

class MemeSession(db.Entity):
    chat_id = Required(int, size=64)
    situation = Required(str)
    status = Required(str, default='lobby')  # lobby, gathering, voting, finished
    entries = Set('MemeEntry')

class MemeEntry(db.Entity):
    player_id = Required(int, size=64)
    player_name = Required(str)
    hand = Required(LongStr)
    sticker_id = Optional(str)
    is_out = Required(bool, default=False) # <--- ПОЛЕ ДЛЯ ВИЛІТУ
    session = Required(MemeSession)
    votes = Set('MemeVote')

class MemeVote(db.Entity):
    voter_id = Required(int, size=64)
    entry = Required(MemeEntry)