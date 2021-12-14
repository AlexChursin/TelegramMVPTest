from http import HTTPStatus
from typing import Optional

import aiohttp
from http import client
import requests
from telegram import config


class MessengerAPI:
    def __init__(self, url):
        self.url = url

    async def get_chat_id(self, dialog_id: int) -> Optional[int]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.url}/chats?dialog_id={dialog_id}') as r:
                if r.status == HTTPStatus.OK:
                    data = await r.json()
                    if len(data):
                        return data[0]['chat_id']
        return None


    async def create_cons(self, chat_id: int, dialog_id: int, username: str) -> Optional[int]:
        body = {
            'dialog_id': dialog_id,
            'tg_firstname': username,
            'chat_id': chat_id
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.url}/chats', data=body) as r:
                if r.status == HTTPStatus.CREATED:
                    data = await r.json()
                    return data['chat_id']
        return None


    async def get_petrovich(self, first_name: str, middle_name: str) -> Optional[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.url}/utils/petrovich?first_name={first_name}&middle_name={middle_name}') as r:
                if r.status == HTTPStatus.OK:
                    data = await r.json()
                    return f"{data['first_name']} {data['middle_name']}"
        return None


mess_api = MessengerAPI(url=config.URL_API_DJANGO)
