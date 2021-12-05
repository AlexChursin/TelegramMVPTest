from datetime import datetime

from .core import Base, metadata, database
import ormar


class UserDB(ormar.Model):
    class Meta:
        tablename = "bot_users"
        metadata = metadata
        database = database

    id: int = ormar.Integer(primary_key=True)
    chat_id: int = ormar.Integer(minimum=0)
    cons_id: int = ormar.Integer(minimum=0, unique=True)
    created: datetime = ormar.DateTime(default=datetime.now)


