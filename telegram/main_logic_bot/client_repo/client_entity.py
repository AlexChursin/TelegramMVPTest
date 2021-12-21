from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .user_bot_state import State


class Consulate(BaseModel):
    user_id: int
    chat_id: Optional[int]
    reason_petition: Optional[str] = None
    select_day: Optional[str] = None
    select_time: Optional[str] = None
    select_schedule_id: Optional[str] = None
    select_is_emergency: bool = False
    dialog_id: Optional[int] = None
    cons_token: Optional[str] = None


class TelegramClient(BaseModel):
    user_id: int
    chat_id: int
    status: int = 1
    age: Optional[int] = None
    phone: Optional[str] = None
    doctor_token: str = None
    doctor_name: str = None
    doctor_name_p: str = None
    client_token: Optional[str] = None
    first_middle_name: Optional[str] = None
    consulate: Optional[Consulate] = None
    consulate_id: Optional[int] = None


@dataclass
class Client:
    def __init__(self, doctor_name: str, doctor_token: str):
        self.doctor_name: str = doctor_name
        self.doctor_token: str = doctor_token
        self.datetime_start = datetime.now()
        self.state: Optional[State] = State.start_first
        self.consulate: ConsulateClient = ConsulateClient()
        self.dialog_id: Optional[int] = None
        self.is_emergency: bool = False
        self.is_memory_user: bool = False

    def __str__(self) -> str:
        return str(self.__dict__)


class ConsulateClient:
    def __init__(self):
        self.day_value: Optional[str] = None
        self.time_value: Optional[str] = None
        self.schedule_id: Optional[int] = None
        self.reason_petition: Optional[str] = None
        self.name_otch: Optional[str] = None
        self.age: Optional[str] = None
        self.number: Optional[str] = None
