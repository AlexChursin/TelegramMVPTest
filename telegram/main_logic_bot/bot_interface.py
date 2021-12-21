from abc import ABC, abstractmethod
from typing import List, Optional

from .bot_entity import InlineViewButton


class IView(ABC):
    @abstractmethod
    async def send_assistant_message(self, chat_id: int, text: str, doctor_n: Optional[str] = None, inline_buttons: List[InlineViewButton] = None,
                                     close_markup: bool = False): ...

    @abstractmethod
    async def send_message_doctor(self, chat_id: int, text: str, doctor_name: str): ...

    @abstractmethod
    async def delete_message(self, chat_id: int, message_id: int): ...

    @abstractmethod
    async def send_phone_request(self, chat_id: int, text: str, doctor_name: str): ...

    @abstractmethod
    async def send_vcard(self, chat_id: int, doctor_name: str, doc_token: str): ...

    @abstractmethod
    async def send_file_from_doctor(self, chat_id: int, data: bytes, filename: str, doctor_name: str): ...

    @abstractmethod
    async def edit_bot_message(self, chat_id: int, text: str, message_id: int,
                               inline_buttons: List[InlineViewButton] = None): ...
