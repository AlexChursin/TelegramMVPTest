from typing import Optional
from .client_entity import StartClientData


class ClientDataProvider:
    user_data = {}

    @staticmethod
    def get_user_obj(user_id: int) -> Optional['StartClientData']:
        if user_id in ClientDataProvider.user_data:
            return ClientDataProvider.user_data[user_id]
        return None

    @staticmethod
    def set_user_obj(user_id: int, from_user: Optional[int] = None):
        ClientDataProvider.user_data[user_id] = StartClientData(from_user)
        return None

