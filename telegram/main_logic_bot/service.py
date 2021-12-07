import logging
from typing import Optional

import api
from .bot_entity import InlineViewButton
from .bot_interface import IView
from .button import ButtonCollection, MyButton
from .config.text_config import TextBot
from .consultate_client_data.client_entity import StartClientData
from .consultate_client_data.client_provider import ClientDataProvider
from .steps.keyboards import get_hello_keyboard, get_change_time_cons_keyboard
from .consultate_client_data.user_bot_state import State

from ..utils import is_number, get_birthday


class BotService:
    def __init__(self, view: IView, text_config: TextBot):
        self.view = view
        self.text_config: TextBot = text_config

    async def send_start_message(self, chat_id: int, user_id: int, refer_url_text: str = ''):
        refer_value = get_refer(refer_url_text)
        doctor_name = api.get_doctor_from_refer(refer_value)
        client = ClientDataProvider.get_client_data(user_id)
        if doctor_name is None:
            is_none = False
            if client is None:
                is_none = True
            else:
                if client.c_doctor_name is None:
                    is_none = True
            if is_none:
                await self.view.send_message(chat_id, 'Зайдите пожалуйста по реферальной ссылке врача')
                return
            else:
                doctor_name = client.c_doctor_name

        text = self.text_config.texts.start.format(str(doctor_name))
        if client is None:
            ClientDataProvider.set_user_obj(user_id, doctor_name)
        else:
            client.update()
        buttons = get_hello_keyboard(self.text_config)
        await self.view.send_message(chat_id, text, inline_buttons=buttons)

    async def send_info(self, chat_id):
        text = self.text_config.texts.info
        await self.view.send_message(chat_id, text)

    async def _send_reason_petition_or_phone_query(self, client, chat_id):
        if client.is_memory_user:
            await self.view.send_message(chat_id, self.text_config.texts.user_reason.format(client.consulate.name_otch),
                                         doctor_n=client.c_doctor_name, close_markup=True)
            client.state = State.await_reason_petition_text
        else:
            await self.view.send_phone_request(chat_id, self.text_config.texts.number,
                                               doctor_name=client.c_doctor_name)
            client.state = State.await_contacts

    async def answer_callback(self, chat_id: int, bot_message_id: int, user_id: int, callback_data: str):
        client = ClientDataProvider.get_client_data(user_id)
        button_object = ButtonCollection.from_callback(callback_data)
        if button_object.type is ButtonCollection.start_button:
            if client is not None:
                client.consulate.day_value = button_object.label.lower()
                list_ = api.get_list_free_times()
                buttons = [InlineViewButton(text=value,
                                            callback=MyButton(value, value,
                                                              ButtonCollection.time_button.value).to_callback()) for
                           value in list_]
                await self.view.edit_bot_message(chat_id,
                                                 text=self.text_config.texts.set_cons_time.format(client.consulate.day_value),
                                                 inline_buttons=buttons,
                                                 message_id=bot_message_id)
        if button_object.type is ButtonCollection.time_button:
            if client is not None:
                client.is_emergency = False
                client.consulate.time_value = button_object.label.lower()
                buttons = get_change_time_cons_keyboard()
                text = self.text_config.texts.cons.format(client.consulate.day_value, client.consulate.time_value)
                await self.view.edit_bot_message(user_id, text=text, inline_buttons=buttons, message_id=bot_message_id)
                await self._send_reason_petition_or_phone_query(client, chat_id)
        if button_object.type is ButtonCollection.start_emergency_button:
            if client is not None:
                client.is_emergency = True
                client.consulate.day_value = None
                client.consulate.time_value = None
                await self._send_reason_petition_or_phone_query(client, chat_id)
        if button_object.type is ButtonCollection.back_main:
            if client is not None:
                await self.view.delete_message(chat_id, bot_message_id)
                await self.view.delete_message(chat_id, bot_message_id + 1)
                await self.send_start_message(chat_id, user_id)

    async def reset_user(self, chat_id: int, user_id: int):
        user = ClientDataProvider.get_client_data(user_id)
        if user is not None:
            ClientDataProvider.set_user_obj(user_id, user.c_doctor_name)
        await self.view.send_message(chat_id, 'Пользователь обновлен')


    async def answer_on_contacts(self, chat_id: int, user_id: int, phone_text: str):
        client = ClientDataProvider.get_client_data(user_id)
        if client is not None:
            client.consulate.number = phone_text
            await self.view.send_message(chat_id, self.text_config.texts.reason, doctor_n=client.c_doctor_name,
                                         close_markup=True)
            client.state = State.await_reason_petition_text

    async def finish(self, chat_id, client):
        if not client.is_emergency:
            send_text = self.text_config.texts.finish.format(client.consulate.day_value.lower(),
                                                             client.consulate.time_value.lower())
        else:
            send_text = self.text_config.texts.finish_emb
        await self.view.send_message(chat_id, text=send_text, doctor_n=client.c_doctor_name)

        dialog_id = api.create_dialog(send_user=client)
        client.is_memory_user = True
        if dialog_id is not None:
            client.dialog_id = dialog_id
            client.state = State.dialog
        else:
            pass  ######### нужно потом написать ответ если диалог не создался 29.11.21

    async def answer_on_any_message(self, chat_id, user_id, text):
        client = ClientDataProvider.get_client_data(user_id)
        if client is None:
            await self.send_start_message(chat_id, user_id)
            return
        if client.state is State.await_contacts:
            if is_number(text):
                client.state = State.dialog
                await self.answer_on_contacts(chat_id, user_id, phone_text=text)
            else:
                await self.view.send_message(chat_id, text=self.text_config.texts.number_error,
                                             doctor_n=client.c_doctor_name)
        elif client.state is State.await_reason_petition_text:
            client.consulate.reason_petition = text
            if client.is_memory_user:
                await self.finish(chat_id, client)
            else:
                await self.view.send_message(chat_id, text=self.text_config.texts.name_otch,
                                             doctor_n=client.c_doctor_name)
                client.state = State.await_name_otch_text

        elif client.state is State.await_name_otch_text:
            client.consulate.name_otch = text
            client.state = State.await_birthday_text
            await self.view.send_message(chat_id, text=self.text_config.texts.birthdate, doctor_n=client.c_doctor_name)
        elif client.state is State.await_birthday_text:
            birthday = get_birthday(text)
            if birthday:
                client.consulate.age = birthday
                await self.finish(chat_id, client)
            else:
                await self.view.send_message(chat_id, text=self.text_config.texts.birthdate_error,
                                             doctor_n=client.c_doctor_name)

        elif client.state is State.dialog:
            if client.dialog_id is not None:
                is_send = api.send_patient_text_message(text=text, dialog_id=client.dialog_id)
                if not is_send:
                    pass  ## нужно написать ответ бота если сообщение не отправлено 29.11.2021


def get_refer(text) -> Optional[str]:
    if ' ' in text:
        try:
            ref_str = text.split(' ')[1]

            return ref_str
        except IndexError:
            logging.warning(f'BAD REFERRAL URL: {text}')
            return None
    return None
