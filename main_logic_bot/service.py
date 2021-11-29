import logging
from typing import Optional

import api
from .bot_entity import InlineViewButton
from .bot_interface import IView
from .button import StartButton, get_button_from_callback, TimeButton
from consultate_client_data.client_provider import ClientDataProvider
from .user_bot_state import State
from config.text_config import TextBot
from utils import is_number


class BotService:
    def __init__(self, view: IView, text_config: TextBot):
        self.view = view
        self.text_config: TextBot = text_config

    def send_start_message(self, chat_id: int, user_id: int, refer_url_text: str = ''):
        from_user = get_refer(refer_url_text)
        if from_user is None:
            user = ClientDataProvider.get_user_obj(user_id)
            is_none = False
            if user is None:
                is_none = True
            else:
                if user.from_user is None:
                    is_none = True
            if is_none:
                self.view.send_message(chat_id, 'Зайдите пожалуйста по реферальной ссылке врача')
                return
            else:
                from_user = user.from_user

        text = self.text_config.start_text.format(str(from_user))
        ClientDataProvider.set_user_obj(user_id, from_user)
        buttons = [InlineViewButton(text=button.name, callback=StartButton(name=button.name, data=button.data).to_str()) for
                   button in self.text_config.start_button_names]
        self.view.send_message(chat_id, text, inline_buttons=buttons)

    def send_info(self, chat_id):
        text = self.text_config.info_text
        self.view.send_message(chat_id, text)

    def answer_callback(self, chat_id: int, user_id: int, callback_data: str):
        user = ClientDataProvider.get_user_obj(user_id)
        button_object = get_button_from_callback(callback_data)
        if isinstance(button_object, StartButton):
            if user is not None:
                user.start_button = button_object
                list_ = api.get_list_free_times()
                buttons = [InlineViewButton(text=value, callback=TimeButton(name=value, data=value).to_str()) for value in
                           list_]
                self.view.send_message(chat_id, text=self.text_config.cons_text, inline_buttons=buttons)
        if isinstance(button_object, TimeButton):
            if user is not None:
                user.time_button = button_object
                self.view.send_message(user_id, text=self.text_config.reason_text)
                user.state = State.await_reason_petition_text

    def answer_on_contacts(self, chat_id: int, user_id: int, phone_text: str):
        user = ClientDataProvider.get_user_obj(user_id)
        if user is not None:
            user.number = phone_text
            send_text = self.text_config.finish.format(user.start_button.name.lower(), user.time_button.name.lower())
            self.view.send_message(chat_id, text=send_text)
            self.view.send_message(chat_id, text=f'Данные для отправки: \n {user}')  # для дебага
            dialog_id = api.create_dialog(send_user=user)
            if dialog_id is not None:
                user.dialog_id = dialog_id
                user.state = State.dialog
            else:
                pass  ######### нужно потом написать ответ если диалог не создался 29.11.21

    def answer_on_any_message(self, chat_id, user_id, text):
        user = ClientDataProvider.get_user_obj(user_id)
        if user is None:
            self.send_start_message(chat_id, user_id)
            return
        if user.state is State.await_reason_petition_text:
            user.reason_petition = text
            user.state = State.await_medication_text
            self.view.send_message(chat_id, text=self.text_config.medications_text)
        elif user.state is State.await_medication_text:
            user.medications = text
            user.state = State.await_family_text
            self.view.send_message(chat_id, text=self.text_config.family_text)
        elif user.state is State.await_family_text:
            user.family = text
            user.state = State.await_name_otch_text
            self.view.send_message(chat_id, text=self.text_config.name_otch_text)
        elif user.state is State.await_name_otch_text:
            user.reason_petition = text
            user.state = State.await_birthday_text
            self.view.send_message(chat_id, text=self.text_config.birthdate_text)
        elif user.state is State.await_birthday_text:
            user.reason_petition = text
            user.state = State.await_contacts
            self.view.send_phone_request(chat_id, text=self.text_config.number_text)
        elif user.state is State.await_contacts:
            if not is_number(text):
                self.view.send_message(chat_id, text=self.text_config.number_error_text)
            else:
                self.answer_on_contacts(chat_id, user_id, phone_text=text)
        elif user.state is State.dialog:
            if user.dialog_id is not None:
                is_send = api.send_patient_text_message(text=text, dialog_id=user.dialog_id)
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
