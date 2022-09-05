import logging
from io import BytesIO
from typing import Optional

import sentry_sdk

from backend_api import back_api
from messenger_api import mess_api
from .bot_interface import IView
from .button import ButtonCollection
from .client_repo.client_interface import IClientRepo
from .client_repo.user_bot_state import State
from .config.text_config import TextBot
from .service_funcs import _get_doctor_from_url
from .steps.keyboards import get_finish_buttons
from ..utils import fix_number


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
            await self.view.send_assistant_message(chat_id, text=self.text_config.texts.error_token)
            return
        if client is None:
            client = await self.client_repo.set_client(user_id=user_id, chat_id=chat_id)
            old_messages = await back_api.get_doctor_messages(dialog_id=cons_info.dialog_id, token=cons_info.cons_token)

        client.doctor_token = cons_info.doc_token
        client.first_middle_name = f'{firstname} {lastname} @{username}'
        client.client_token = cons_info.patient_token
        await self._send_old_mes(old_messages, chat_id, cons_info.doctor_name)

        if client.phone:
            api_data = await back_api.send_confirm_cons(cons_token=cons_info.cons_token,
                                                        first_name=firstname,
                                                        middle_name=lastname,
                                                        phone=client.phone)
            if api_data['ok']:
                client.status = State.dialog.value
                client.consulate = await self.client_repo.new_consulate(user_id, chat_id)
                client.consulate.reason_petition = 'web'
                client.consulate.dialog_id = cons_info.dialog_id
                client.doctor_name = cons_info.doctor_name
                client.consulate.select_is_emergency = cons_info.is_emergency
                client.consulate.cons_token = cons_info.cons_token
                await self.view.send_assistant_message(chat_id, text=self.text_config.texts.continue_dialog.format(
                    doctor_name=cons_info.doctor_name))
            else:
                await self.view.send_assistant_message(chat_id, text=api_data['error']['text'])
        else:
            client.consulate = await self.client_repo.new_consulate(user_id, chat_id)
            client.consulate.reason_petition = 'web'
            client.consulate.dialog_id = cons_info.dialog_id
            client.doctor_name = cons_info.doctor_name
            client.consulate.select_is_emergency = cons_info.is_emergency
            client.consulate.cons_token = cons_info.cons_token

            client.status = State.await_contacts.value
            await self.view.send_phone_request(chat_id, self.text_config.texts.number)
        await self.client_repo.save_client(client)

    async def _send_old_mes(self, old_messages, chat_id, doctor_name):
        for mes in old_messages:
            if mes['type'] == 'text':
                await self.view.send_message_doctor(chat_id, text=mes['text'],
                                                    doctor_name=doctor_name)
            if mes['type'] == 'file':
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
            await self.send_recommend(user_id=user_id, chat_id=chat_id)
        if button_object.type is ButtonCollection.new_query:
            client.status = State.start_first.value
            client.consulate = None
        await self.client_repo.save_client(client)

    async def answer_on_any_message(self, chat_id, user_id, text):
        client = await self.client_repo.get_client(user_id)
        if client is None:
            await self.answer_on_start_command(chat_id, user_id)
            return
        elif client.status is State.start_first.value:
            await self.answer_on_start_command(chat_id, user_id)
            return
        elif client.status is State.await_contacts.value:
            await self.view.send_phone_request(chat_id, self.text_config.texts.number)
            return
        elif client.status is State.dialog.value and client.consulate:
            if client.consulate.dialog_id:
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
            # buttons = get_button_new_con(self.text_config.buttons.new_cons) if add_buttons else None
            await self.view.send_assistant_message(chat_id=chat_id, text=self.text_config.texts.recommend_friend)
            await self.view.send_vcard(chat_id=chat_id, doctor_name=client.doctor_name, doc_token=client.doctor_token)

    async def finish_consulate(self, user_id, chat_id, text: str) -> Optional[int]:
        client = await mess_api.get_client(user_id=user_id)
        if client:
            await self.view.send_assistant_message(chat_id=chat_id, text=text,
                                                   inline_buttons=get_finish_buttons(
                                                       self.text_config.buttons.recommend_friend,
                                                       self.text_config.buttons.new_query,
                                                       url_new_cons=f'https://doc-crm.net/?doc_token={client.doctor_token}'))
            client.status = State.start_first.value
            client.consulate = None
            await self.client_repo.save_client(client)
            return client.chat_id
        return None

    async def reset_user(self, chat_id: int, user_id: int):
        client = await self.client_repo.set_client(chat_id, user_id)
        if client:
            await self.view.send_assistant_message(chat_id, text=f"Пользователь {client.chat_id} сброшен")

    async def answer_on_contacts(self, user_id: int, chat_id: int, phone_text: str, firstname: str, lastname: str):
        client = await self.client_repo.get_client(user_id)
        if client is not None:
            if client.status is State.await_contacts.value and client.consulate:
                client.phone = fix_number(phone_text)
                client.status = State.dialog.value
                api_data = await back_api.send_confirm_cons(cons_token=client.consulate.cons_token,
                                                            first_name=firstname,
                                                            middle_name=lastname,
                                                            phone=client.phone)

                if not api_data['ok']:
                    await self.view.send_assistant_message(chat_id, text=api_data['error']['text'])
                else:
                    client.consulate = None
                    client.status = State.start_first.value
                    await self.view.send_assistant_message(chat_id, text=self.text_config.texts.continue_dialog.format(
                        doctor_name=client.doctor_name))
                await self.client_repo.save_client(client)
            else:
                await self.view.send_assistant_message(chat_id, text=self.text_config.texts.error_token)

    async def send_message_doctor(self, chat_id, text: str, doctor_name: str):
        await self.view.send_message_doctor(chat_id=chat_id, text=text, doctor_name=doctor_name)

    async def send_file_from_doctor(self, chat_id, data: bytes, filename: str, doctor_name: str):
        await self.view.send_file_from_doctor(chat_id=chat_id, data=data, filename=filename, doctor_name=doctor_name)
