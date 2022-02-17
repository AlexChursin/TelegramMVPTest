from abc import ABC, abstractmethod
from typing import List, Optional

from .bot_entity import InlineViewButton, ViewButton


class IView(ABC):
    @abstractmethod
    async def send_assistant_message(self, chat_id: int, text: str, inline_buttons: List[InlineViewButton] = None, buttons: List[ViewButton] = None, close_buttons: bool = False): ...

    @abstractmethod
    async def send_message_doctor(self, chat_id: int, text: str, doctor_name: str): ...


    @abstractmethod
    async def send_vcard(self, chat_id: int, doctor_name: str, doc_token: str): ...

    @abstractmethod
    async def send_file_from_doctor(self, chat_id: int, data: Optional[bytes], filename: str, doctor_name: str): ...

