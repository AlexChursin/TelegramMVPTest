from typing import Optional

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
    get_finish_cons_buttons, get_button_new_con
from ..utils import is_number, get_birthday, fix_number


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

    async def _send_doctor_hello_message(self, client: TelegramClient, token: str, doctor_name_p: str, edit: bool = False, message_id: Optional[int]= None):
        list_key_days = await back_api.get_list_free_days(doc_token=token)
        buttons = None
        if len(list_key_days):
            text = self.text_config.texts.start.format(str(doctor_name_p))
            show_ember = False
            if client.client_token and not client.consulate:
                show_ember = True
            buttons = get_hello_keyboard(self.text_config, show_ember, list_key_days)
        else:
            text = self.text_config.texts.start_empty.format(str(doctor_name_p))
        if not edit:
            await self.view.send_assistant_message(client.chat_id, text, inline_buttons=buttons)
        else:
            await self.view.edit_bot_message(client.chat_id, text, message_id=message_id, inline_buttons=buttons)

    async def _old_client(self, client: TelegramClient, refer_url_text: str = ''):
        if client.consulate:
            if client.consulate.cons_token:  # идет консультация
                if not client.consulate.select_is_emergency:
                    await self.view.send_assistant_message(client.chat_id, self.text_config.texts.sorry_dialog_now.format(
                        client.consulate.select_day,
                        client.consulate.select_time.split()[0],
                        client.consulate.select_time.split()[1],
                        client.doctor_name
                    ), doctor_n=client.doctor_name_p)
                else:
                    await self.view.send_assistant_message(client.chat_id, self.text_config.texts.sorry_dialog_now_emer.format(
                        client.doctor_name), doctor_n=client.doctor_name_p)
                return
        doctor_name, doctor_name_p, token = await _get_doctor_from_url(refer_url_text)
        if doctor_name is not None:
            await self.client_repo.set_client(client.user_id, chat_id=client.chat_id, status=State.start_first.value,
                                              doctor_name=doctor_name, doc_token=token,
                                              doctor_name_p=doctor_name_p)
            await self._send_doctor_hello_message(client, token, doctor_name_p)
        else:
            await self._send_doctor_hello_message(client, client.doctor_token, client.doctor_name_p)

    async def _new_client(self, chat_id: int, user_id: int, refer_url_text: str = ''):
        doctor_name, doctor_name_p, token = await _get_doctor_from_url(refer_url_text)
        if doctor_name is not None:
            client = await self.client_repo.set_client(user_id=user_id, chat_id=chat_id, status=State.start_first.value,
                                                       doctor_name=doctor_name, doc_token=token,
                                                       doctor_name_p=doctor_name_p)
            await self._send_doctor_hello_message(client, token, doctor_name_p)
        else:
            await self.view.send_assistant_message(chat_id, self.text_config.texts.error_token)

    async def answer_on_start_command(self, chat_id: int, user_id: int, refer_url_text: str = '', username: str = '',
                                      firstname: str = '', lastname: str = ''):
        client = await self.client_repo.get_client(user_id)
        if client is not None:
            await self._old_client(client)
        else:
            await self._new_client(chat_id, user_id, refer_url_text)

    async def send_info(self, chat_id):
        text = self.text_config.texts.info
        await self.view.send_assistant_message(chat_id, text)

    async def _send_reason_petition_or_phone_query(self, client: TelegramClient, chat_id) -> TelegramClient:
        if client.phone:
            await self.view.send_assistant_message(chat_id,
                                                   self.text_config.texts.user_reason.format(client.first_middle_name),
                                                   doctor_n=client.doctor_name_p)
            client.status = State.await_reason_petition_text.value
        else:
            await self.view.send_phone_request(chat_id, self.text_config.texts.number,
                                               doctor_name=client.doctor_name_p)
            client.status = State.await_contacts.value
        return client

    async def answer_callback(self, chat_id: int, bot_message_id: int, user_id: int, callback_data: str):
        client = await self.client_repo.get_client(user_id)
        if client is None:
            await self.answer_on_start_command(chat_id, user_id)
            return
        button_object = ButtonCollection.from_callback(callback_data)
        if button_object.type is ButtonCollection.start_b:
            client.consulate = await self.client_repo.new_consulate(user_id, chat_id)
            client.consulate.select_day = button_object.label.lower()
            list_times = await back_api.get_list_free_times(day=button_object.data, doc_token=client.doctor_token)
            await self.view.edit_bot_message(chat_id,
                                             text=self.text_config.texts.set_cons_time.format(
                                                 client.consulate.select_day),
                                             inline_buttons=get_time_buttons(list_times),
                                             message_id=bot_message_id)
        if button_object.type is ButtonCollection.time_button:
            client.consulate.select_time = button_object.label.lower()
            client.consulate.select_schedule_id = int(button_object.data)
            buttons = get_change_time_cons_keyboard(self.text_config.buttons.change_time_cons)
            text = self.text_config.texts.cons.format(client.consulate.select_day, client.consulate.select_time)
            await self.view.edit_bot_message(chat_id=chat_id, text=text, inline_buttons=buttons,
                                             message_id=bot_message_id)
            client = await self._send_reason_petition_or_phone_query(client, chat_id)
        if button_object.type is ButtonCollection.back_time_to_main:
            client.consulate = None
            await self._send_doctor_hello_message(client, client.doctor_token, client.doctor_name_p, edit=True, message_id=bot_message_id)
        if button_object.type is ButtonCollection.start_emer_b:
            client.consulate = await self.client_repo.new_consulate(user_id, chat_id)
            client.consulate.select_is_emergency = True
            client = await self._send_reason_petition_or_phone_query(client, chat_id)
        if button_object.type is ButtonCollection.back_main:
            await self.view.delete_message(chat_id, bot_message_id)
            await self.view.delete_message(chat_id, bot_message_id + 1)
            await self.answer_on_start_command(chat_id, user_id)
        if button_object.type is ButtonCollection.recommend_friends:
            await self.view.send_assistant_message(chat_id=chat_id, text=self.text_config.texts.recommend_friend, doctor_n=client.doctor_name, buttons=get_button_new_con(self.text_config.buttons.new_cons))
            await self.view.send_vcard(chat_id=chat_id, doctor_name=client.doctor_name, doc_token=client.doctor_token)
        if button_object.type is ButtonCollection.new_query:
            client.status = State.start_first.value
            await self.answer_on_start_command(chat_id, user_id)
        await self.client_repo.save_client(client)

    async def reset_user(self, chat_id: int, user_id: int):
        # client = self.client_repo.get_client(user_id)
        # self.client_repo.set_client(user_id, client.doctor_name, client.doctor_token)
        # self.client_repo.save_client(client)
        await self.view.send_assistant_message(chat_id, 'Пользователь обновлен')

    async def answer_on_contacts(self, chat_id: int, user_id: int, phone_text: str):
        client = await self.client_repo.get_client(user_id)
        if client is not None:
            client.phone = fix_number(phone_text)
            await self.view.send_assistant_message(chat_id, self.text_config.texts.reason, doctor_n=client.doctor_name)
            client.status = State.await_reason_petition_text.value
        await self.client_repo.save_client(client)

    async def _finish(self, chat_id, client: TelegramClient) -> TelegramClient:
        if not client.consulate.select_is_emergency:
            send_text = self.text_config.texts.finish.format(
                client.consulate.select_day,
                client.consulate.select_time.split()[0],
                client.consulate.select_time.split()[1])
        else:
            send_text = self.text_config.texts.finish_emb
        res = await back_api.create_consulate(chat_id, client=client)
        if res:
            await self.view.send_assistant_message(chat_id, text=send_text, doctor_n=client.doctor_name,
                                                   buttons=get_finish_cons_buttons(self.text_config.buttons.reject_consulate))

            dialog_id, cons_token, client_token = res
            client.consulate.dialog_id = dialog_id
            client.consulate.cons_token = cons_token
            client.client_token = client_token
            client.status = State.dialog.value
        else:
            await self.view.send_assistant_message(chat_id, text=self.text_config.texts.error_create_cons,
                                                   doctor_n=client.doctor_name)
            pass  ######### нужно потом написать ответ если диалог не создался 29.11.21
        return client

    async def answer_on_any_message(self, chat_id, user_id, text):
        client = await self.client_repo.get_client(user_id)
        if client is None:
            await self.answer_on_start_command(chat_id, user_id)
            return
        else:
            if client.status is State.start_first.value:
                await self.answer_on_start_command(chat_id, user_id)
                return
            if client.status is State.await_contacts.value:
                if is_number(text):
                    client.status = State.dialog.value
                    await self.answer_on_contacts(chat_id, user_id, phone_text=text)
                else:
                    await self.view.send_assistant_message(chat_id, text=self.text_config.texts.number_error,
                                                           doctor_n=client.doctor_name)
            elif client.status is State.await_reason_petition_text.value:
                client.consulate.reason_petition = text
                if client.first_middle_name:
                    client = await self._finish(chat_id, client)
                else:
                    await self.view.send_assistant_message(chat_id, text=self.text_config.texts.name_otch,
                                                           doctor_n=client.doctor_name)
                    client.status = State.await_name_otch_text.value

            elif client.status is State.await_name_otch_text.value:
                client.first_middle_name = text
                client.status = State.await_birthday_text.value
                await self.view.send_assistant_message(chat_id, text=self.text_config.texts.birthdate,
                                                       doctor_n=client.doctor_name)
            elif client.status is State.await_birthday_text.value:
                birthday = get_birthday(text)
                if birthday:
                    client.age = birthday
                    client = await self._finish(chat_id, client)
                else:
                    await self.view.send_assistant_message(chat_id, text=self.text_config.texts.birthdate_error,
                                                           doctor_n=client.doctor_name)

            elif client.status is State.dialog.value:
                if text == self.text_config.buttons.reject_consulate:
                    await back_api.send_reject_cons(client.client_token, client.consulate.cons_token)
                    await self.view.send_assistant_message(chat_id, text=self.text_config.texts.reject_consulate, close_buttons=True)
                    client.status = State.start_first.value
                    client.consulate = None
                    await self._send_doctor_hello_message(client, client.doctor_token, client.doctor_name_p)
                else:
                    if client.consulate.dialog_id is not None:
                        is_send = await back_api.send_patient_text_message(text=text, dialog_id=client.consulate.dialog_id)
                        if not is_send:
                            pass  ## нужно написать ответ бота если сообщение не отправлено 29.11.2021
            await self.client_repo.save_client(client)
