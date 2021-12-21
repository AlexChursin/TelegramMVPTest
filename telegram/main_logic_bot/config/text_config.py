from dataclasses import dataclass
from pydantic import BaseModel


class Button(BaseModel):
    label: str
    key: str


class Texts(BaseModel):
    start: str
    start_empty: str
    info: str
    set_cons_time: str
    cons: str
    user_reason: str
    reason: str
    medications: str
    family: str
    name_otch: str
    birthdate: str
    birthdate_error: str
    number: str
    number_error: str
    finish: str
    finish_emb: str
    sorry_dialog_now: str
    error_token: str
    error_create_cons: str


class Buttons(BaseModel):
    start_button_now: Button
    start_button_tomorrow: Button
    start_button_emergency: Button


class TextBot(BaseModel):
    texts: Texts
    buttons: Buttons
