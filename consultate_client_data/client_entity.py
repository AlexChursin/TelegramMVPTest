from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from main_logic_bot.button import StartButton, TimeButton
from main_logic_bot.user_bot_state import State


@dataclass
class StartClientData:
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
        self.dialog_id: Optional[int] = None

    def __str__(self) -> str:
        return str(self.__dict__)
