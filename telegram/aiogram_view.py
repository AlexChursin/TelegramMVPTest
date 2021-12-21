from io import BytesIO

from aiogram import Bot, types
from aiogram.types import InlineKeyboardMarkup, InputFile
from sentry_sdk import capture_exception

from .bot_init import bot
from .config import BOT_NAME
from .main_logic_bot.bot_entity import InlineViewButton
from .main_logic_bot.bot_interface import IView

from typing import List, Optional


class TelegramView(IView):
    async def send_vcard(self, chat_id: int, doctor_name: str, doc_token: str):
        await self._bot.send_contact(chat_id, phone_number='+11111111111', first_name=doctor_name.split()[0],
                                     last_name=doctor_name.split()[0],
                                     vcard="BEGIN:VCARD\n" +
                                           "VERSION:3.0\n" +
                                           "N:Solo;Han\n" +
                                           # "ORG:Организация ассистент\n" +
                                           f"URL:https://t.me/{BOT_NAME}?start=doc_{doc_token}\n"
                                           "TEL;TYPE=voice,work,pref:+111111111111\n" +
                                           # "EMAIL:hansolo@mfalcon.com\n" +
                                           "END:VCARD")

    async def send_message_doctor(self, chat_id: int, text: str, doctor_name: str):
        text = f"<b>{doctor_name}</b>\n{text}"
        await self._bot.send_message(chat_id, text=text, parse_mode='HTML')

    def __init__(self, bot_: Bot):
        self._bot: Bot = bot_

    async def send_file_from_doctor(self, chat_id: int, data: bytes, filename: str, doctor_name: str):
        try:
            b = BytesIO(data)
            await self._bot.send_document(chat_id, b, caption=filename)
        except Exception as e:
            capture_exception(e)

    async def delete_message(self, chat_id: int, message_id: int):
        await self._bot.delete_message(chat_id, message_id=message_id)

    @staticmethod
    def __get_markup(inline_buttons: List[InlineViewButton], close_markup: bool = False) -> InlineKeyboardMarkup:
        markup = types.ReplyKeyboardRemove() if close_markup else None

        if inline_buttons is not None:
            markup = types.InlineKeyboardMarkup(row_width=1)
            for button in inline_buttons:
                markup.add(types.InlineKeyboardButton(text=button.text, callback_data=button.callback))
        return markup

    async def edit_bot_message(self, chat_id: int, text: str, message_id: int,
                               inline_buttons: List[InlineViewButton] = None):
        markup = self.__get_markup(inline_buttons)
        await self._bot.edit_message_text(chat_id=chat_id,
                                          text=text,
                                          message_id=message_id,
                                          reply_markup=markup,
                                          parse_mode='HTML')

    async def send_phone_request(self, chat_id: int, text: str, doctor_name: str):
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(types.KeyboardButton(text='Передать номер телефона', request_contact=True))
        if doctor_name is not None:
            text = f'Ассистент <b>{doctor_name}:</b>\n{text}'
        await self._bot.send_message(chat_id, text=text, reply_markup=markup, parse_mode='HTML')

    async def send_assistant_message(self, chat_id: int, text: str,
                                     doctor_n: Optional[str] = None,
                                     inline_buttons: List[InlineViewButton] = None,
                                     close_markup: bool = False):
        print(chat_id)
        markup = self.__get_markup(inline_buttons, close_markup)
        if doctor_n is not None:
            text = f'Ассистент <b>{doctor_n}:</b>\n{text}'
        await self._bot.send_message(chat_id, text=text, reply_markup=markup, parse_mode='HTML')


tg_view = TelegramView(bot)
