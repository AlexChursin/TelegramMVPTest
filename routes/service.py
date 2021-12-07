from typing import Optional
from ormar import NoMatch
from db.model import UserDB
from telegram.main_logic_bot.consultate_client_data.client_entity import StartClientData


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
