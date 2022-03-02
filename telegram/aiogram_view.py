from io import BytesIO
from typing import List, Optional

from aiogram import Bot, types
from aiogram.types import InlineKeyboardMarkup, InputFile

from .bot_init import bot
from .config import BOT_NAME
from .main_logic_bot.bot_entity import InlineViewButton, ViewButton
from .main_logic_bot.bot_interface import IView


class TelegramView(IView):
    async def send_vcard(self, chat_id: int, doctor_name: str, doc_token: str):
        await self._bot.send_contact(chat_id, phone_number='+11111111111', first_name=doctor_name.split()[0],
                                     last_name=doctor_name.split()[1],
                                     vcard="BEGIN:VCARD\n" +
                                           "VERSION:3.0\n" +
                                           # "N:Solo;Han\n" +
                                           "NOTE:Новая консультация\n" +
                                           # "ORG:Организация ассистент\n" +
                                           f"URL:https://doc-crm.net/?doc_token={doc_token}\n" +
                                           # f"URL:https://t.me/{BOT_NAME}?start=doc_{doc_token}\n"
                                           # "TEL;TYPE=celular:*\n" +
                                           # "EMAIL:hansolo@mfalcon.com\n" +
                                           "END:VCARD")

    async def send_message_doctor(self, chat_id: int, text: str, doctor_name: str):
        text = f"<b>{doctor_name}:</b>\n{text}"
        markup = types.ReplyKeyboardRemove()
        await self._bot.send_message(chat_id, text=text, parse_mode='HTML', reply_markup=markup)

    async def send_phone_request(self, chat_id: int, text: str):
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton(text='Передать номер телефона', request_contact=True))
        await self._bot.send_message(chat_id, text=text, reply_markup=markup, parse_mode='HTML')

    def __init__(self):
        self._bot: Bot = bot

    async def send_file_from_doctor(self, chat_id: int, data: Optional[bytes], filename: str, doctor_name: str):
        if data:
            b = BytesIO(data)
            await self._bot.send_document(chat_id, document=InputFile(b), caption=filename)

    async def delete_message(self, chat_id: int, message_id: int):
        await self._bot.delete_message(chat_id, message_id=message_id)

    @staticmethod
    def __get_markup(inline_buttons: List[InlineViewButton] = None, buttons: List[ViewButton] = None,
                     close_buttons: bool = False) -> Optional[InlineKeyboardMarkup]:
        markup = types.ReplyKeyboardRemove()

        if inline_buttons is not None:
            markup = types.InlineKeyboardMarkup(row_width=1)
            for button in inline_buttons:
                markup.add(types.InlineKeyboardButton(text=button.text, url=button.url, callback_data=button.callback))
        if buttons is not None:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for button in buttons:
                markup.add(types.KeyboardButton(text=button.text))
        if close_buttons:
            markup = types.ReplyKeyboardRemove()

        return markup

    async def send_assistant_message(self, chat_id: int, text: str,
                                     inline_buttons: List[InlineViewButton] = None, buttons: List[ViewButton] = None,
                                     close_buttons: bool = False):
        print(chat_id)
        markup = self.__get_markup(inline_buttons, buttons, close_buttons)

        await self._bot.send_message(chat_id, text=text, reply_markup=markup, parse_mode='HTML')
