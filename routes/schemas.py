from enum import Enum

from pydantic import BaseModel, Field


class ErrorMessage(BaseModel):
    detail: str


class Message(BaseModel):
    chat_id: int = Field(1, description='чат привязанный к консультации')

