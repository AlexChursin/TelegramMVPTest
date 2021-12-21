from enum import Enum, auto
from typing import List, Optional

from telegram.main_logic_bot.bot_entity import InlineViewButton
from telegram.main_logic_bot.bot_interface import IView


class Answers:
    last: Optional[str]


class TestView(IView):

    async def send_assistant_message(self, chat_id: int, text: str, doctor_n: Optional[str] = None,
                                     inline_buttons: List[InlineViewButton] = None, close_markup: bool = False):
        Answers.last = text

    async def send_message_doctor(self, chat_id: int, text: str, doctor_name: str):
        Answers.last = text

    async def delete_message(self, chat_id: int, message_id: int):
        Answers.last = None

    async def send_phone_request(self, chat_id: int, text: str, doctor_name: str):
        Answers.last = text

    async def send_file_from_doctor(self, chat_id: int, data: bytes, filename: str, doctor_name: str):
        Answers.last = None

    async def edit_bot_message(self, chat_id: int, text: str, message_id: int,
                               inline_buttons: List[InlineViewButton] = None):
        Answers.last = text
