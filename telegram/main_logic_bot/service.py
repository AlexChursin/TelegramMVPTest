import logging
from typing import Optional

from backend import back_api
from messenger_api import mess_api
from .bot_interface import IView
from .button import ButtonCollection
from .client_repo.client_entity import Client
from .client_repo.client_interface import IClientRepo
from .config.text_config import TextBot
from .steps.keyboards import get_hello_keyboard, get_change_time_cons_keyboard, get_start_button
from .client_repo.user_bot_state import State
from ..utils import is_number, get_birthday
import sentry_sdk

sentry_sdk.init(
    "https://800a5e93aeac4323a5a12b23870eb917@o1091110.ingest.sentry.io/6107767",
    traces_sample_rate=1.0,
)


class BotService:
    def __init__(self, view: IView, text_config: TextBot, client_repo: IClientRepo):
        self.view: IView = view
        self.text_config: TextBot = text_config
        self.client_repo: IClientRepo = client_repo

    async def send_start_message(self, chat_id: int, user_id: int, refer_url_text: str = ''):
        refer_value = get_refer(refer_url_text)
        doctor = await back_api.get_doctor(refer_value)
        doctor_name = None
        if doctor is not None:
            first_name, middle_name = doctor.split()
            doctor_name = mess_api.get_petrovich(first_name, middle_name)
        client = self.client_repo.get_client_data(user_id)
        if doctor_name is None:
            is_none = False
            if client is None:
                is_none = True
            else:
                if client.doctor_name is None:
                    is_none = True
            if is_none:
                await self.view.send_message(chat_id, 'Зайдите пожалуйста по реферальной ссылке врача')
                return

        text = self.text_config.texts.start.format(str(doctor_name))
        self.client_repo.set_client(user_id, doctor_name, doctor_name)
        list_key_days = back_api.get_list_free_days(doc_token=client.doc_token)
        buttons = get_hello_keyboard(self.text_config, list_key_days)
        await self.view.send_message(chat_id, text, inline_buttons=buttons)
        self.client_repo.save_client(client)

    async def send_info(self, chat_id):
        text = self.text_config.texts.info
        await self.view.send_message(chat_id, text)

    async def _send_reason_petition_or_phone_query(self, client, chat_id):
        if client.is_memory_user:
            await self.view.send_message(chat_id, self.text_config.texts.user_reason.format(client.consulate.name_otch),
                                         doctor_n=client.doctor_name, close_markup=True)
            client.state = State.await_reason_petition_text
        else:
            await self.view.send_phone_request(chat_id, self.text_config.texts.number,
                                               doctor_name=client.doctor_name)
            client.state = State.await_contacts
            

    async def answer_callback(self, chat_id: int, bot_message_id: int, user_id: int, callback_data: str):
        client = self.client_repo.get_client_data(user_id)
        button_object = ButtonCollection.from_callback(callback_data)
        if button_object.type is ButtonCollection.start_button:
            if client is not None:
                client.consulate.day_value = button_object.label.lower()
                list_times = back_api.get_list_free_times(day=button_object.data, doc_token=client.doc_token)
                await self.view.edit_bot_message(chat_id,
                                                 text=self.text_config.texts.set_cons_time.format(
                                                     client.consulate.day_value),
                                                 inline_buttons=get_start_button(list_times),
                                                 message_id=bot_message_id)
        if button_object.type is ButtonCollection.time_button:
            if client is not None:
                client.consulate.time_value = button_object.label.lower()
                client.consulate.schedule_id = int(button_object.data)
                buttons = get_change_time_cons_keyboard()
                text = self.text_config.texts.cons.format(client.consulate.day_value, client.consulate.time_value)
                await self.view.edit_bot_message(chat_id=chat_id, text=text, inline_buttons=buttons, message_id=bot_message_id)
                await self._send_reason_petition_or_phone_query(client, chat_id)
        if button_object.type is ButtonCollection.start_emergency_button:
            if client is not None:
                client.is_emergency = True
                client.consulate.day_value = None
                client.consulate.time_value = None
                client.consulate.schedule_id = None
                await self._send_reason_petition_or_phone_query(client, chat_id)
        if button_object.type is ButtonCollection.back_main:
            if client is not None:
                await self.view.delete_message(chat_id, bot_message_id)
                await self.view.delete_message(chat_id, bot_message_id + 1)
                await self.send_start_message(chat_id, user_id)
        self.client_repo.save_client(client)

    async def reset_user(self, chat_id: int, user_id: int):
        client = self.client_repo.get_client_data(user_id)
        self.client_repo.set_client(user_id, client.doctor_name, client.doc_token)
        self.client_repo.save_client(client)
        await self.view.send_message(chat_id, 'Пользователь обновлен')


    async def answer_on_contacts(self, chat_id: int, user_id: int, phone_text: str):
        client = self.client_repo.get_client_data(user_id)
        if client is not None:
            client.consulate.number = phone_text
            await self.view.send_message(chat_id, self.text_config.texts.reason, doctor_n=client.doctor_name,
                                         close_markup=True)
            client.state = State.await_reason_petition_text
        self.client_repo.save_client(client)

    async def _finish(self, chat_id, client):
        if not client.is_emergency:
            send_text = self.text_config.texts.finish.format(client.consulate.day_value.lower(),
                                                             client.consulate.time_value.lower())
        else:
            send_text = self.text_config.texts.finish_emb
        await self.view.send_message(chat_id, text=send_text, doctor_n=client.doctor_name)

        dialog_id = await back_api.create_dialog(chat_id, client=client)
        client.is_memory_user = True
        if dialog_id is not None:
            client.dialog_id = dialog_id
            client.state = State.dialog
        else:
            pass  ######### нужно потом написать ответ если диалог не создался 29.11.21

    async def answer_on_any_message(self, chat_id, user_id, text):
        client = self.client_repo.get_client_data(user_id)
        if client is None:
            await self.send_start_message(chat_id, user_id)
            return
        if client.state is State.start_first:
            await self.send_start_message(chat_id, user_id)
        if client.state is State.await_contacts:
            if is_number(text):
                client.state = State.dialog
                await self.answer_on_contacts(chat_id, user_id, phone_text=text)
            else:
                await self.view.send_message(chat_id, text=self.text_config.texts.number_error,
                                             doctor_n=client.doctor_name)
        elif client.state is State.await_reason_petition_text:
            client.consulate.reason_petition = text
            if client.is_memory_user:
                await self._finish(chat_id, client)
            else:
                await self.view.send_message(chat_id, text=self.text_config.texts.name_otch,
                                             doctor_n=client.doctor_name)
                client.state = State.await_name_otch_text

        elif client.state is State.await_name_otch_text:
            client.consulate.name_otch = text
            client.state = State.await_birthday_text
            await self.view.send_message(chat_id, text=self.text_config.texts.birthdate, doctor_n=client.doctor_name)
        elif client.state is State.await_birthday_text:
            birthday = get_birthday(text)
            if birthday:
                client.consulate.age = birthday
                await self._finish(chat_id, client)
            else:
                await self.view.send_message(chat_id, text=self.text_config.texts.birthdate_error,
                                             doctor_n=client.doctor_name)

        elif client.state is State.dialog:
            if client.dialog_id is not None:
                is_send = back_api.send_patient_text_message(text=text, dialog_id=client.dialog_id)
                if not is_send:
                    pass  ## нужно написать ответ бота если сообщение не отправлено 29.11.2021
        self.client_repo.save_client(client)


def get_refer(text) -> Optional[str]:
    if ' ' in text:
        try:
            ref_str = text.split(' ')[1]

            return ref_str
        except IndexError:
            logging.warning(f'BAD REFERRAL URL: {text}')
            return None
    return None
