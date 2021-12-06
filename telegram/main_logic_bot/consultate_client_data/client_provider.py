from typing import Optional
from .client_entity import StartClientData


class ClientDataProvider:
    _clients = {}

    @staticmethod
    def get_client_state(user_id: int) -> Optional['StartClientData']:
        if user_id in ClientDataProvider._clients:
            return ClientDataProvider._clients[user_id]
        return None

    @staticmethod
    def set_user_obj(user_id: int, doctor_name: Optional[str] = None):
        ClientDataProvider._clients[user_id] = StartClientData(doctor_name)
        return None

