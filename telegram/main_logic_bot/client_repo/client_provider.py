
from typing import Optional
from .client_entity import Client
from .client_interface import IClientRepo


class MemoryClientRepo(IClientRepo):
    def save_client(self, client: Client) -> bool:
        pass

    def __init__(self):
        self._clients = {}


    def get_client_data(self, user_id: int) -> Optional['Client']:
        if user_id in self._clients:
            return self._clients[user_id]
        return None

    def set_client(self, user_id: int, doctor_name: str, doc_token: str):
        # time_two_hour_ago = datetime.now() - 3600 * 120
        # for k, client in ClientDataProvider._clients.items():
        #     if client.datetime_start < time_two_hour_ago and not client.is_memory_user:
        #         ClientDataProvider._clients.pop(k)
        self._clients[user_id] = Client(doctor_name, doc_token)
        return None



