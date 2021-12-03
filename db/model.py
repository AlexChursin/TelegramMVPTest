import sqlalchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from .core import Base, metadata

DBUsers = sqlalchemy.Table(
    "bot_users",
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('cons_id', String, unique=True),
    Column('chat_id', String, index=True),
    Column('created', DateTime, server_default=func.now()),
    Column('updated', DateTime, onupdate=func.now())
)
