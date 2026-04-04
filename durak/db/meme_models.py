from pony.orm import Required, Optional, Set, PrimaryKey
from .database import db

class MemeSession(db.Entity):
    chat_id = Required(int, size=64)
    situation = Required(str)
    status = Required(str, default='gathering') # gathering, voting, finished
    entries = Set('MemeEntry')

class MemeEntry(db.Entity):
    player_id = Required(int, size=64)
    player_name = Required(str)
    sticker_id = Required(str)
    session = Required(MemeSession)
    votes = Set('MemeVote')

class MemeVote(db.Entity):
    voter_id = Required(int, size=64)
    entry = Required(MemeEntry)