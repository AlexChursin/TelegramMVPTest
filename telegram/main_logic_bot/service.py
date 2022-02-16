import logging
from http import HTTPStatus
from io import BytesIO
from typing import Optional

import requests
import sentry_sdk

from backend_api import back_api
from messenger_api import mess_api
from .bot_interface import IView
from .button import ButtonCollection
from .client_repo.client_entity import TelegramClient
from .client_repo.client_interface import IClientRepo
from .client_repo.user_bot_state import State
from .config.text_config import TextBot
from .service_funcs import _get_doctor_from_url
from .steps.keyboards import get_hello_keyboard, get_change_time_cons_keyboard, get_time_buttons, \
    get_finish_cons_buttons, get_button_new_con, get_finish_buttons

from ..utils import is_number, fix_number, is_first_middle_name


def traces_sampler(sampling_context):
    return 1


sentry_sdk.init(
    "https://800a5e93aeac4323a5a12b23870eb917@o1091110.ingest.sentry.io/6107767",
    traces_sample_rate=1.0,
    traces_sampler=traces_sampler
)


class BotService:
    def __init__(self, view: IView, text_config: TextBot, client_repo: IClientRepo):
        self.view: IView = view
        self.text_config: TextBot = text_config
        self.client_repo: IClientRepo = client_repo

    async def answer_on_start_command(self, chat_id: int, user_id: int, refer_url_text: str = '', username: str = '',
                                      firstname: str = '', lastname: str = ''):
        client = await self.client_repo.get_client(user_id)
        old_messages = []
        cons_info = await _get_doctor_from_url(refer_url_text)
        if cons_info is None:
            return
        if client is None:
            client = await self.client_repo.set_client(user_id=user_id, chat_id=chat_id)
            old_messages = await back_api.get_doctor_messages(dialog_id=cons_info.dialog_id, token=cons_info.doc_token)
        client.status = State.dialog.value
        client.doctor_token = cons_info.doc_token
        client.client_token = cons_info.patient_token
        client.consulate = await self.client_repo.new_consulate(user_id, chat_id)
        client.consulate.reason_petition = 'web'
        client.consulate.dialog_id = cons_info.dialog_id
        client.consulate.select_is_emergency = cons_info.is_emergency
        client.consulate.cons_token = cons_info.cons_token
        await self.view.send_message_doctor(chat_id, text=self.text_config.texts.continue_dialog,
                                            doctor_name=cons_info.doctor_name)

        await self._send_old_mes(old_messages, chat_id, cons_info.doctor_name)
        await self.client_repo.save_client(client)

    async def _send_old_mes(self, old_messages, chat_id, doctor_name):
        for mes in old_messages:
            if mes['_type'] == 'text':
                await self.view.send_message_doctor(chat_id, text=mes['text'],
                                                    doctor_name=doctor_name)
            if mes['_type'] == 'file':
                await self.view.send_file_from_doctor(chat_id,
                                                      data=await back_api.get_file_bytes(mes['file']['path']),
                                                      doctor_name=doctor_name,
                                                      filename=mes['file']['name'])

    async def send_help(self, chat_id):
        text = self.text_config.texts.help
        await self.view.send_assistant_message(chat_id, text)

    async def answer_callback(self, chat_id: int, user_id: int, callback_data: str):
        client = await self.client_repo.get_client(user_id)
        if client is None:
            await self.answer_on_start_command(chat_id, user_id)
            return
        button_object = ButtonCollection.from_callback(callback_data)
        if button_object.type is ButtonCollection.recommend_friends:
            await self.send_recommend(user_id=user_id, chat_id=chat_id, add_buttons=True)
        if button_object.type is ButtonCollection.new_query:
            client.status = State.start_first.value
            await self.answer_on_start_command(chat_id, user_id)
        await self.client_repo.save_client(client)

    async def answer_on_any_message(self, chat_id, user_id, text):
        client = await self.client_repo.get_client(user_id)
        if client is None:
            await self.answer_on_start_command(chat_id, user_id)
            return
        if client.status is State.start_first.value:
            await self.answer_on_start_command(chat_id, user_id)
            return

        elif client.status is State.dialog.value and client.consulate:
            if text == self.text_config.buttons.reject_consulate:
                await back_api.send_reject_cons(client.client_token, client.consulate.cons_token)
                await self.view.send_assistant_message(chat_id, text=self.text_config.texts.reject_consulate,
                                                       close_buttons=True)
                client.status = State.start_first.value
                client.consulate = None
                await self.client_repo.save_client(client)
                await self.answer_on_start_command(chat_id, user_id)
            elif client.consulate.dialog_id is not None:
                is_send = await back_api.send_patient_text_message(text=text,
                                                                   dialog_id=client.consulate.dialog_id)
                if not is_send:
                    logging.error('сообщение врачу не отправлено')

    async def send_file_to_doctor(self, user_id, filename: str, bytes_oi: BytesIO):
        client = await self.client_repo.get_client(user_id)
        if client:
            if client.consulate:
                if client.consulate.dialog_id:
                    await back_api.send_patient_document(dialog_id=client.consulate.dialog_id, filename=filename,
                                                         data=bytes_oi)

    async def send_recommend(self, user_id, chat_id, add_buttons: bool = False):
        client = await self.client_repo.get_client(user_id)
        if client:
            buttons = get_button_new_con(self.text_config.buttons.new_cons) if add_buttons else None
            await self.view.send_assistant_message(chat_id=chat_id, text=self.text_config.texts.recommend_friend,
                                                   buttons=buttons)
            await self.view.send_vcard(chat_id=chat_id, doctor_name=client.doctor_name, doc_token=client.doctor_token)

    async def finish_consulate(self, user_id, chat_id, text: str) -> Optional[int]:
        client = await mess_api.get_client(user_id=user_id)
        if client:
            await self.view.send_assistant_message(chat_id=chat_id, text=text,
                                                   inline_buttons=get_finish_buttons(
                                                       self.text_config.buttons.recommend_friend,
                                                       self.text_config.buttons.new_query))
            client.status = State.start_first.value
            client.consulate = None
            await self.client_repo.save_client(client)
            return client.chat_id
        return None

    async def send_message_doctor(self, chat_id, text: str, doctor_name: str):
        await self.view.send_message_doctor(chat_id=chat_id, text=text, doctor_name=doctor_name)

    async def send_file_from_doctor(self, chat_id, data: bytes, filename: str, doctor_name: str):
        await self.view.send_file_from_doctor(chat_id=chat_id, data=data, filename=filename, doctor_name=doctor_name)
