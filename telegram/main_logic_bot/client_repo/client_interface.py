from abc import ABC, abstractmethod
from typing import Optional
from .client_entity import Client, TelegramClient, Consulate


class IClientRepo(ABC):
    @abstractmethod
    async def set_client(self, user_id: int, chat_id: int) -> Optional[TelegramClient]: ...

    @abstractmethod
    async def get_client(self, user_id: int) -> Optional[TelegramClient]: ...

    @abstractmethod
    async def new_consulate(self, user_id: int, chat_id: int) -> Consulate: ...

    @abstractmethod
    async def save_client(self, client: TelegramClient) -> Optional[TelegramClient]: ...

