from typing import List

from pydantic import BaseModel


class Button(BaseModel):
    name: str
    data: str


class TextBot(BaseModel):
    start_text: str
    info_text: str
    start_button_names: List[Button]
    cons_text: str
    reason_text: str
    medications_text: str
    family_text: str
    name_otch_text: str
    birthdate_text: str
    number_text: str
    number_error_text: str
    finish: str



