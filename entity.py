from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from button_models import StartButton, TimeButton


class SendDataProvider:
    user_data = {}

    @staticmethod
    def get_user_obj(user_id: int) -> Optional['SendUserData']:
        if user_id in SendDataProvider.user_data:
            return SendDataProvider.user_data[user_id]
        return None

    @staticmethod
    def set_user_obj(user_id: int, from_user: int | None = None):
        SendDataProvider.user_data[user_id] = SendUserData(from_user)
        return None


@dataclass
class SendUserData:
    def __init__(self, from_user: int | None = None):
        self.from_user = from_user
        self.datetime_start = datetime.now()
        self.start_button: StartButton | None = None
        self.time_button: TimeButton | None = None
        self.reason_petition: str | None = None
        self.medications: str | None = None
        self.family: str | None = None
        self.name_otch: str | None = None
        self.birthday: str | None = None
        self.number: str | None = None
    def __str__(self) -> str:
        return str(self.__dict__)