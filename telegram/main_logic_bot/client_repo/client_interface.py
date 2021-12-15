from abc import ABC, abstractmethod
from typing import Optional
from .client_entity import Client


class IClientRepo(ABC):
    @abstractmethod
    def set_client(self, user_id: int, doctor_name: str, doc_token: str): ...

    @abstractmethod
    def get_client_data(self, user_id: int) -> Optional[Client]: ...

    @abstractmethod
    def save_client(self, client: Client) -> bool: ...

