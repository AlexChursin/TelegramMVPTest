from http import HTTPStatus
from typing import Optional

from messenger_api import mess_api, MessengerAPI
from .client_entity import TelegramClient, Consulate
from .client_interface import IClientRepo

#
# class MemoryClientRepo(IClientRepo):
#     def new_consulate(self, user_id: int) -> Consulate:
#         pass
#
#     def save_client(self, client: TelegramClient) -> bool:
#         self._clients[client.user_id] = client
#         return True
#
#     def __init__(self):
#         self._clients = {}
#
#     def get_client(self, user_id: int) -> Optional[TelegramClient]:
#         if user_id in self._clients:
#             return self._clients[user_id]
#         return None
#
#     def new_client(self, user_id: int, chat_id: int, status: int, doctor_name: str, doctor_name_p: str, doc_token: str) -> bool:
#         self._clients[user_id] = TelegramClient(user_id=user_id, chat_id=chat_id, status=status,
#                                                 doctor_token=doc_token, doctor_name=doctor_name)
#         return True


class APIClientRepo(IClientRepo):
    def __init__(self):
        self.api: MessengerAPI = mess_api

    async def new_consulate(self, user_id: int, chat_id: int) -> Consulate:
        consulate = Consulate(user_id=user_id, chat_id=chat_id)
        client = await self.api.new_consulate(user_id, consulate)
        return client.consulate


    async def get_client(self, user_id: int) -> Optional[TelegramClient]:
        return await self.api.get_client(user_id)

    async def set_client(self, user_id: int, chat_id: int) -> Optional[TelegramClient]:
        client = TelegramClient(user_id=user_id, chat_id=chat_id)
        is_updated = await self.api.update_client(client)

        if is_updated:
            return client
        return None

    async def save_client(self, client: TelegramClient) -> Optional[TelegramClient]:
        is_updated = await self.api.update_client(client)
        if is_updated:
            return client
        return None
