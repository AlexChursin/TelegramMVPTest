import json
import os
import threading
from typing import List, Optional

from pip import __main__
from telebot.types import Message, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telebot import types, TeleBot
from main_logic_bot.bot_entity import InlineViewButton
from main_logic_bot.bot_interface import IView
from main_logic_bot.service import BotService
from config.text_config import TextBot

KEY = os.environ.get('TELEGRAM_TOKEN')
bot: TeleBot = TeleBot(KEY)


class TelegramView(IView):

    def delete_message(self, chat_id: int, message_id: int):
        self._bot.delete_message(chat_id, message_id=message_id)

    def __init__(self):
        self._bot: TeleBot = bot

    @staticmethod
    def __get_markup(inline_buttons: List[InlineViewButton], close_markup: bool = False) -> InlineKeyboardMarkup:
        markup = types.ReplyKeyboardRemove() if close_markup else None

        if inline_buttons is not None:
            markup = types.InlineKeyboardMarkup(row_width=1)
            for button in inline_buttons:
                markup.add(types.InlineKeyboardButton(text=button.text, callback_data=button.callback))
        return markup

    def edit_bot_message(self, chat_id: int, text: str, message_id: int, inline_buttons: List[InlineViewButton] = None):
        markup = self.__get_markup(inline_buttons)
        self._bot.edit_message_text(chat_id=chat_id,
                                    text=text,
                                    message_id=message_id,
                                    reply_markup=markup,
                                    parse_mode='HTML')

    def send_phone_request(self, chat_id: int, text: str):
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(types.KeyboardButton(text='Передать номер телефона', request_contact=True))

        self._bot.send_message(chat_id, text=text, reply_markup=markup, parse_mode='HTML')

    def send_message(self, chat_id: int, text: str,
                     inline_buttons: List[InlineViewButton] = None,
                         close_markup: bool = False):
        markup = self.__get_markup(inline_buttons, close_markup)
        self._bot.send_message(chat_id, text=text, reply_markup=markup, parse_mode='HTML')


bot_service = BotService(view=TelegramView(),
                         text_config=TextBot(**json.load(open('config/bot_text_word.json', 'r', encoding='UTF-8'))))


@bot.message_handler(commands=['start'])
def on_start_command(message: Message):
    bot_service.send_start_message(chat_id=message.chat.id, user_id=message.from_user.id,
                                   refer_url_text=message.text)


@bot.message_handler(commands=['info'])
def info_message(message):
    bot_service.send_info(chat_id=message.chat.id)


@bot.message_handler(func=lambda message: True)
def text_message(message: Message):
    bot_service.answer_on_any_message(chat_id=message.chat.id, user_id=message.from_user.id, text=message.text)


@bot.callback_query_handler(func=lambda call: True)
def inline(call: CallbackQuery):
    bot_service.answer_callback(chat_id=call.message.chat.id,
                                bot_message_id=call.message.message_id,
                                user_id=call.from_user.id, callback_data=call.data)
    bot.answer_callback_query(call.id, text='')


@bot.message_handler(content_types=['contact'])
def contact(message: Message):
    if message.contact is not None:
        bot_service.answer_on_contacts(message.chat.id, message.from_user.id, message.contact.phone_number)
    else:
        pass


def start_telegram_bot():
    tr = threading.Thread(target=bot.polling, args=[True])
    while True:
        tr.run()
        tr = threading.Thread(target=bot.polling, args=[True])


def start_telegram_bot_in_new_thread():
    threading.Thread(target=start_telegram_bot).start()


if __name__ == "__main__":
    start_telegram_bot()
