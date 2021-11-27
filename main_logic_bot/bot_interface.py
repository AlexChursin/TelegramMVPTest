from abc import ABC, abstractmethod
from typing import List

from .bot_entity import  InlineViewButton


class IView(ABC):
    @abstractmethod
    def send_message(self, chat_id: int, text: str, inline_buttons: List[InlineViewButton] = None): ...

    @abstractmethod
    def send_phone_request(self, chat_id: int, text: str): ...
