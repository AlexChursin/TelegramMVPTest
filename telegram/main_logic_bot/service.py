import logging
from typing import Optional

import api
from .bot_entity import InlineViewButton
from .bot_interface import IView
from .button import ButtonCollection, MyButton
from .config.text_config import TextBot
from .consultate_client_data.client_provider import ClientDataProvider
from .steps.hello import get_hello_keyboard
from .consultate_client_data.user_bot_state import State

from ..utils import is_number, get_birthday


class BotService:
    def __init__(self, view: IView, text_config: TextBot):
        self.view = view
        self.text_config: TextBot = text_config

    async def send_start_message(self, chat_id: int, user_id: int, refer_url_text: str = ''):
        refer_value = get_refer(refer_url_text)
        from_user = api.get_user_from_refer(refer_value)
        user = ClientDataProvider.get_user_obj(user_id)
        if from_user is None:
            is_none = False
            if user is None:
                is_none = True
            else:
                if user.from_user is None:
                    is_none = True
            if is_none:
                await self.view.send_message(chat_id, 'Зайдите пожалуйста по реферальной ссылке врача')
                return
            else:
                from_user = user.from_user

        text = self.text_config.texts.start.format(str(from_user))
        if user is None:
            ClientDataProvider.set_user_obj(user_id, from_user)
        buttons = get_hello_keyboard(self.text_config)
        await self.view.send_message(chat_id, text, inline_buttons=buttons)

    async def send_info(self, chat_id):
        text = self.text_config.texts.info
        await self.view.send_message(chat_id, text)

    async def answer_callback(self, chat_id: int, bot_message_id: int, user_id: int, callback_data: str):
        user = ClientDataProvider.get_user_obj(user_id)
        button_object = ButtonCollection.from_callback(callback_data)
        if button_object.type is ButtonCollection.start_button:
            if user is not None:
                user.day_value = button_object.label.lower()
                list_ = api.get_list_free_times()
                buttons = [InlineViewButton(text=value,
                                            callback=MyButton(value, value,
                                                              ButtonCollection.time_button.value).to_callback()) for
                           value in list_]
                await self.view.edit_bot_message(chat_id,
                                                 text=self.text_config.texts.set_cons_time.format(user.day_value),
                                                 inline_buttons=buttons,
                                                 message_id=bot_message_id)
        if button_object.type is ButtonCollection.time_button:
            if user is not None:
                user.time_value = button_object.label.lower()
                callback_back_b = MyButton('back', 'back', type_value=ButtonCollection.back_main.value).to_callback()
                buttons = [InlineViewButton(text="Изменить время консультации", callback=callback_back_b)]
                text = self.text_config.texts.cons.format(user.day_value, user.time_value)
                await self.view.edit_bot_message(user_id, text=text, inline_buttons=buttons, message_id=bot_message_id)
                await self.view.send_phone_request(chat_id, self.text_config.texts.number)
                user.is_emergency = False
                user.state = State.await_contacts

        if button_object.type is ButtonCollection.start_emergency_button:
            if user is not None:
                user.is_emergency = True
                user.day_value = None
                user.time_value = None
                await self.view.send_phone_request(chat_id, self.text_config.texts.number)
                user.state = State.await_contacts


        if button_object.type is ButtonCollection.back_main:
            if user is not None:
                await self.view.delete_message(chat_id, bot_message_id)
                await self.view.delete_message(chat_id, bot_message_id + 1)
                await self.send_start_message(chat_id, user_id)

    async def answer_on_contacts(self, chat_id: int, user_id: int, phone_text: str):
        user = ClientDataProvider.get_user_obj(user_id)
        if user is not None:
            user.number = phone_text
            if user.cons_finish:
                await self.view.send_message(chat_id, self.text_config.texts.user_reason.format(user.name_otch),close_markup=True)
            else:
                await self.view.send_message(chat_id, self.text_config.texts.reason, close_markup=True)
            user.state = State.await_reason_petition_text

    def finish(self, user):
        dialog_id = api.create_dialog(send_user=user)
        user.cons_finish = True
        if dialog_id is not None:
            user.dialog_id = dialog_id
            user.state = State.dialog
        else:
            pass  ######### нужно потом написать ответ если диалог не создался 29.11.21

    async def answer_on_any_message(self, chat_id, user_id, text):
        user = ClientDataProvider.get_user_obj(user_id)
        if user is None:
            await self.send_start_message(chat_id, user_id)
            return
        if user.state is State.await_contacts:
            if is_number(text):
                user.state = State.dialog
                await self.answer_on_contacts(chat_id, user_id, phone_text=text)
            else:
                await self.view.send_message(chat_id, text=self.text_config.texts.number_error)
        elif user.state is State.await_reason_petition_text:
            user.reason_petition = text
            user.state = State.await_medication_text
            await self.view.send_message(chat_id, text=self.text_config.texts.medications)
        elif user.state is State.await_medication_text:
            user.medications = text
            if user.cons_finish:
                if user.is_emergency:
                    send_text = self.text_config.texts.finish_emb
                else:
                    send_text = self.text_config.texts.finish.format(user.day_value.lower(),
                                                                     user.time_value.lower())
                await self.view.send_message(chat_id, text=send_text)
                self.finish(user)
            else:
                await self.view.send_message(chat_id, text=self.text_config.texts.name_otch)
                user.state = State.await_name_otch_text

        elif user.state is State.await_name_otch_text:
            user.name_otch = text
            user.state = State.await_birthday_text
            await self.view.send_message(chat_id, text=self.text_config.texts.birthdate)
        elif user.state is State.await_birthday_text:
            birthday = get_birthday(text)
            if birthday:
                user.birthday = birthday
                if not user.is_emergency:
                    send_text = self.text_config.texts.finish.format(user.day_value.lower(),
                                                                     user.time_value.lower())
                else:
                    send_text = self.text_config.texts.finish_emb
                await self.view.send_message(chat_id, text=send_text)
                self.finish(user)
            else:
                await self.view.send_message(chat_id, text=self.text_config.texts.birthdate_error)

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
