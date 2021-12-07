from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .user_bot_state import State


@dataclass
class StartClientData:
    def __init__(self, doctor_name: str = None):
        self.c_doctor_name: str = doctor_name
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
        self.reason_petition: Optional[str] = None
        self.name_otch: Optional[str] = None
        self.age: Optional[str] = None
        self.number: Optional[str] = None
