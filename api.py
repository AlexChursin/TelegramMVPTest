from http import HTTPStatus
from typing import List, Optional

import aiohttp
import requests

from telegram.config import URL_API_BACKEND
from telegram.main_logic_bot.consultate_client_data.client_entity import StartClientData


class API:
    def __init__(self, url):
        self.url = url

    async def get_doctor_from_refer(self, value: str = None):
        if value is not None:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.url}/doctor?token={value}') as r:
                    if r.status == HTTPStatus.OK:
                        try:
                            res = await r.json()
                            doctor = res['data']
                            return f"{doctor['first_name']} {doctor['middle_name']}"
                        except:
                            pass
        else:
            return None


    def create_dialog(self, send_user: StartClientData) -> Optional[int]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.url}/doctor?token={value}') as r:
                if r.status == HTTPStatus.OK:
                    try:
                        res = await r.json()
                        doctor = res['data']
                        return f"{doctor['first_name']} {doctor['middle_name']}"
                    except:
                        pass
        return 1


    def get_list_free_times(self) -> List[str]:
        requests.get(f'{self.url}/xxx')
        return ['14:00', '17:15']


    def send_patient_text_message(self, text: str, dialog_id: int):
        return True


back_api = API(url=URL_API_BACKEND)
