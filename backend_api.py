import logging
from datetime import datetime, timedelta
from http import HTTPStatus
from io import BytesIO
from typing import List, Optional, Tuple

import aiohttp
from aiohttp import FormData
from sentry_sdk import capture_exception

from telegram.config import URL_API_BACKEND
from telegram.main_logic_bot.bot_entity import Schedule
from telegram.main_logic_bot.client_repo.client_entity import TelegramClient


class API:
    def __init__(self, url):
        self.url = url

    async def get_doctor_name(self, token: str = None) -> Optional[str]:
        try:
            if token is not None:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'{self.url}/doctor?token={token}') as r:
                        if r.status == HTTPStatus.OK:
                            res = await r.json()
                            doctor = res['data']
                            return f"{doctor['first_name']} {doctor['middle_name']}"
                        return 'Кристина Александровна'
            else:
                return None
        except Exception as e:
            capture_exception(e)
        return None


    async def create_consulate(self, chat_id: int, client: TelegramClient, ) -> Optional[Tuple[int, str, str]]:
        """
        :return:Id диалога и токен клиента
        """
        try:
            first_name, middle_name = client.first_middle_name.split()
            if not client.client_token:
                body = {
                    "doc_token": client.doctor_token,
                    "session_uid": str(chat_id),
                    "platform": 2,
                    "reason": client.consulate.reason_petition,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "phone": client.phone,
                    "schedule_id": client.consulate.select_schedule_id
                }
            else:
                body = {
                    "doc_token": client.doctor_token,
                    "session_uid": str(chat_id),
                    "platform": 2,
                    "reason": client.consulate.reason_petition,
                    "patient_token": client.client_token,
                }
                if not client.consulate.select_is_emergency:
                    body['schedule_id'] = int(client.consulate.select_schedule_id)

            async with aiohttp.ClientSession() as session:
                async with session.post(f'{self.url}/consultation', json=body) as r:
                    json = await r.json()  # debug
                    if r.status == HTTPStatus.OK:
                        res = await r.json()
                        return res['data']['dialog_id'], res['data']['cons_token'], res['data']['patient_token']
                    else:
                        logging.error(f'body: {body}, {json}')
                    return None
        except Exception as e:
            capture_exception(e)
        return None

    async def get_list_free_days(self, doc_token: str) -> List[str]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.url}/schedule?doc_token={doc_token}') as r:
                    if r.status == HTTPStatus.OK:
                        res = await r.json()
                        data = res['data']
                        if len(data):
                            return [str(key) for key, value in data.items() if len(value)]
                        else:
                            return []
        except Exception as e:
            capture_exception(e)
        return []

    async def get_list_free_times(self, day: str, doc_token: str) -> List[Schedule]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.url}/schedule?doc_token={doc_token}') as r:
                    if r.status == HTTPStatus.OK:
                        res = await r.json()
                        data = res['data'][day]
                        _format = '%H:%M'
                        _list_time = [datetime.fromisoformat(val['date'][:-1]) for val in data]
                        list_times = [f'{time.strftime(_format)} {(time + timedelta(hours=1)).strftime(_format)}' for time
                                      in _list_time]
                        return [Schedule(id=val['id'], time=list_times[i]) for i, val in enumerate(data)]
        except Exception as e:
            capture_exception(e)
        return []

    async def send_patient_text_message(self, text: str, dialog_id: int):
        try:
            body = {
                "_type": "text",
                "data": {
                    "text": text
                }
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(f'{self.url}/dialog/{dialog_id}/message', json=body) as r:
                    if r.status == HTTPStatus.OK:
                        res = await r.json()
                        return res['data']
                    return None
        except Exception as e:
            capture_exception(e)
        return None

    async def send_patient_document(self, dialog_id: int, filename: str, data: BytesIO) -> bool:
        try:
            form_data = FormData()
            form_data.add_field('file', data, filename=filename)
            async with aiohttp.ClientSession() as session:
                async with session.post(f'{self.url}/dialog/{dialog_id}/upload', data=form_data) as r:
                    if r.status == HTTPStatus.OK:
                        return True
                    return False
        except Exception as e:
            capture_exception(e)
        return False

    async def send_reject_cons(self, client_token: str, cons_token: str):
        try:
            body = {
                "cons_token": client_token,
                "patient_token": cons_token
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(f'{self.url}/consultation/reject', json=body) as r:
                    if r.status == HTTPStatus.OK:
                        await r.json()
        except Exception as e:
            capture_exception(e)


back_api = API(url=URL_API_BACKEND)
