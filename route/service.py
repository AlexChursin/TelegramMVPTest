from sqlite3 import IntegrityError
from typing import Optional

from db.core import database
from db.model import DBUsers


async def get_chat_id(cons_id: int) -> Optional[int]:
    query = DBUsers.select().where(DBUsers.cons_id == cons_id)
    db_notes = await database.fetch_all(query)
    if db_notes is not None:
        return db_notes[-1]
    return None


async def create_cons(chat_id: int, cons_id: int) -> Optional[int]:
    r = DBUsers.insert(values=(cons_id, chat_id))
    try:
        last_record_id = await database.execute(r)
    except IntegrityError:
        DBUsers.update(values=(cons_id, chat_id))
        return
    return last_record_id
