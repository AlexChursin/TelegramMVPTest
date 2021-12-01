from typing import Optional

from db.core import database
from db.model import User


async def get_chat_id(cons_id: int) -> Optional[int]:
    query = User.select().where(User.cons_id == cons_id)
    db_notes = await database.fetch_all(query)
    if db_notes is not None:
        return db_notes[-1]
    return None


async def create_cons(chat_id: int) -> Optional[int]:
    query = User(chat_id=1)
    note = await database.fetch_one(query)
    if note is not None:
        return note[-1]
    return None
