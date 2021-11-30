from abc import ABC, abstractmethod
from typing import List

from .bot_entity import InlineViewButton


class IView(ABC):
    @abstractmethod
    def send_message(self, chat_id: int, text: str, inline_buttons: List[InlineViewButton] = None,
                         close_markup: bool = False): ...

    @abstractmethod
    def delete_message(self, chat_id: int,  message_id: int): ...

    @abstractmethod
    def send_phone_request(self, chat_id: int, text: str): ...

    @abstractmethod
    def edit_bot_message(self, chat_id: int, text: str, message_id: int,
                         inline_buttons: List[InlineViewButton] = None): ...