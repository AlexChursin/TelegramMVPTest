from datetime import datetime
from typing import Optional
from .client_entity import StartClientData


class ClientDataProvider:
    _clients = {}

    @staticmethod
    def get_client_data(user_id: int) -> Optional['StartClientData']:
        if user_id in ClientDataProvider._clients:
            return ClientDataProvider._clients[user_id]
        return None

    @staticmethod
    def set_user_obj(user_id: int, doctor_name: Optional[str] = None):
        # time_two_hour_ago = datetime.now() - 3600 * 120
        # for k, client in ClientDataProvider._clients.items():
        #     if client.datetime_start < time_two_hour_ago and not client.is_memory_user:
        #         ClientDataProvider._clients.pop(k)
        ClientDataProvider._clients[user_id] = StartClientData(doctor_name)
        return None

