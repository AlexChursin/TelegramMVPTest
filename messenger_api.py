from http import HTTPStatus
from typing import Optional

import aiohttp
from telegram import config
from telegram.main_logic_bot.client_repo.client_entity import TelegramClient, Consulate


class MessengerAPI:
    def __init__(self, url):
        self.url = url

    async def get_client(self, user_id) -> Optional[TelegramClient]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.url}/tg/client/{user_id}') as r:
                if r.status == HTTPStatus.OK:
                    data = await r.json()
                    return TelegramClient(**data)
        return None

    async def get_consulate(self, dialog_id) -> Optional[Consulate]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.url}/tg/consulate/dialog/{dialog_id}') as r:
                if r.status == HTTPStatus.OK:
                    data = await r.json()
                    return Consulate(**data)
        return None

    async def new_consulate(self, user_id, consulate: Consulate) -> Optional[TelegramClient]:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.url}/tg/client/{user_id}/consulate', data=consulate.json()) as r:
                if r.status == HTTPStatus.CREATED:
                    data = await r.json()
                    return TelegramClient(**data)
        return None


    async def new_client(self, client: TelegramClient) -> Optional[TelegramClient]:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.url}/tg/client', data=client.json()) as r:
                if r.status == HTTPStatus.CREATED:
                    await r.json()
                    return TelegramClient(**await r.json())
                if r.status == HTTPStatus.CONFLICT:
                    return None
        return None

    async def update_client(self, client: TelegramClient) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.put(f'{self.url}/tg/client/{client.user_id}', data=client.json()) as r:
                if r.status == HTTPStatus.OK:
                    await r.json()
                    return True
                if r.status == HTTPStatus.NOT_FOUND:
                    return False
        return False


    async def get_petrovich(self, first_name, middle_name) -> Optional[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.url}/utils/petrovich?first_name={first_name}&middle_name={middle_name}') as r:
                if r.status == HTTPStatus.OK:
                    data = await r.json()
                    return f"{data['first_name']} {data['middle_name']}"
        return None


mess_api = MessengerAPI(url=config.URL_API_DJANGO)
