from enum import Enum

from pydantic import BaseModel, Field


class Petrovich(BaseModel):
    first_name: str
    middle_name: str
    last_name: str


class Padej(str, Enum):
    GENITIVE = 'родительный'
    DATIVE = 'дательный'
    ACCUSATIVE = 'винительный'
    INSTRUMENTAL = 'творительный'
    PREPOSITIONAL = 'предложный'


class MyGender(str, Enum):
    MALE = 'он'
    FEMALE = 'она'
    ANDROGYNOUS = 'оно'

class ErrorMessage(BaseModel):
    detail: str


class Message(BaseModel):
    chat_id: int = Field(1, description='чат привязанный к консультации')

