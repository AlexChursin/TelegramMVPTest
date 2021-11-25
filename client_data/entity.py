from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from logic.button import StartButton, TimeButton
from logic.user_state import State


class ClientDataProvider:
    user_data = {}

    @staticmethod
    def get_user_obj(user_id: int) -> Optional['SendClientData']:
        if user_id in ClientDataProvider.user_data:
            return ClientDataProvider.user_data[user_id]
        return None

    @staticmethod
    def set_user_obj(user_id: int, from_user: Optional[int] = None):
        ClientDataProvider.user_data[user_id] = SendClientData(from_user)
        return None


@dataclass
class SendClientData:
    def __init__(self, from_user: Optional[int] = None):
        self.from_user = from_user
        self.datetime_start = datetime.now()
        self.start_button: StartButton | None = None
        self.time_button: TimeButton | None = None
        self.reason_petition: Optional[str] = None
        self.medications: Optional[str] = None
        self.family: Optional[str] = None
        self.name_otch: Optional[str] = None
        self.birthday: Optional[str] = None
        self.number: Optional[str] = None
        self.state: Optional[State] = State.start_first

    def __str__(self) -> str:
        return str(self.__dict__)
