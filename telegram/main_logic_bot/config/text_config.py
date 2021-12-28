from dataclasses import dataclass
from pydantic import BaseModel


class Button(BaseModel):
    label: str
    key: str


class Texts(BaseModel):
    start: str
    start_empty: str
    help: str
    set_cons_time: str
    cons: str
    user_reason: str
    reason: str
    name_otch: str
    birthdate: str
    birthdate_error: str
    number: str
    number_error: str
    finish: str
    finish_emb: str
    recommend_friend: str
    sorry_dialog_now: str
    sorry_dialog_now_emer: str
    reject_consulate: str
    error_token: str
    error_create_cons: str


class Buttons(BaseModel):
    start_button_now: str
    start_button_tomorrow: str
    start_button_emergency: str
    change_time_cons: str
    reject_consulate: str
    new_cons: str
    recommend_friend: str
    new_query: str

class TextBot(BaseModel):
    texts: Texts
    buttons: Buttons
