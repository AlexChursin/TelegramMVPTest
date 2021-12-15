from datetime import datetime, timedelta
from http import HTTPStatus
from typing import List, Optional

import aiohttp
import requests
from pydantic import BaseModel

from telegram.config import URL_API_BACKEND
from telegram.main_logic_bot.bot_entity import Schedule
from telegram.main_logic_bot.client_repo.client_entity import Client

class API:
    def __init__(self, url):
        self.url = url

    async def get_doctor(self, token: str = None):
        if token is not None:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.url}/doctor?token={token}') as r:
                    if r.status == HTTPStatus.OK:
                        try:
                            res = await r.json()
                            doctor = res['data']
                            return f"{doctor['first_name']} {doctor['middle_name']}"
                        except:
                            pass
        else:
            return None

    async def create_dialog(self, chat_id: int, client: Client) -> Optional[int]:
        first_name, middle_name = client.consulate.name_otch.split()
        body = {
            "doc_token": client.doc_token,
            "session_uid": str(chat_id),
            "platform": 2,
            "schedule_id": client.consulate.schedule_id,
            "reason": client.consulate.reason_petition,
            "medication_current": "None",
            "first_name": first_name,
            "middle_name": middle_name,
            "age": client.consulate.age,
            "phone": client.consulate.number
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.url}/consultation', data=body) as r:
                if r.status == HTTPStatus.OK:
                    try:
                        res = await r.json()
                        return res['data']['dialog_id']
                    except:
                        pass
        return None

    def get_list_free_times(self, day: str, doc_token: str) -> List[Schedule]:
        data = requests.get(f'{self.url}/schedule?doc_token={doc_token}').json()['data'][day]
        _format = '%H:%M'
        _list_time = [datetime.fromisoformat(val['date'][:-1]) for val in data]
        list_times = [f'{(time + timedelta(hours=1)).strftime(_format)} {time.strftime(_format)}' for time in _list_time]
        return [Schedule(id=val['id'], time=list_times[i]) for i, val in enumerate(data)]

    def get_list_free_days(self, doc_token: str) -> List[str]:
        r = requests.get(f'{self.url}/schedule?doc_token={doc_token}')
        data = r.json()['data']
        return [str(day) for day in data.keys()]

    def send_patient_text_message(self, text: str, dialog_id: int):
        return True


back_api = API(url=URL_API_BACKEND)
