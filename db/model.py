import sqlalchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime

from .core import metadata, Base


class User(Base):
    __tablename__ = "bot_users"

    id = Column(Integer, primary_key=True, index=True)
    cons_id = Column(String, unique=True)
    chat_id = Column(String, index=True)
    datetime = Column(DateTime, )
