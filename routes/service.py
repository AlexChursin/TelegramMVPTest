from sqlite3 import IntegrityError
from typing import Optional

from ormar import NoMatch
from telegram.bot_controller import bot, dp
from db.core import database
from db.model import UserDB


async def get_chat_id(cons_id: int) -> Optional[int]:
    try:
        user = await UserDB.objects.filter(cons_id=cons_id).first()
        return user.chat_id
    except NoMatch:
        return None


async def create_cons(chat_id: int, cons_id: int) -> Optional[int]:
    try:
        user = await UserDB.objects.get(cons_id=cons_id)
        if user.chat_id != chat_id:
            await user.update(chat_id=chat_id)
    except NoMatch:
        user = await UserDB.objects.create(cons_id=cons_id, chat_id=chat_id)
    return user.id


