import json
import os
from typing import List, Optional
from telebot.types import Message, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telebot import types, TeleBot
from main_logic_bot.bot_entity import InlineViewButton
from main_logic_bot.bot_interface import IView
from main_logic_bot.service import BotService
from config.text_config import TextBot

KEY = os.environ.get('TELEGRAM_TOKEN')
bot: TeleBot = TeleBot(KEY)


class TelegramView(IView):

    def __init__(self):
        self._bot: TeleBot = bot

    @staticmethod
    def __get_markup(inline_buttons: List[InlineViewButton]) -> InlineKeyboardMarkup:
        markup = types.ReplyKeyboardRemove()
        if inline_buttons is not None:
            markup = types.InlineKeyboardMarkup(row_width=1)
            for button in inline_buttons:
                markup.add(types.InlineKeyboardButton(text=button.text, callback_data=button.callback, ))
        return markup

    def edit_bot_message(self, chat_id: int, text: str, message_id: int, inline_buttons: List[InlineViewButton] = None):
        # bot.edit_message_text(chat_id=chat_id,
        #                       text='text',
        #                       message_id=message.message_id,
        #                       reply_markup=None,
        #                       parse_mode='HTML')
        markup = self.__get_markup(inline_buttons)
        self._bot.edit_message_text(chat_id=chat_id,
                                    text=text,
                                    message_id=message_id,
                                    reply_markup=markup,
                                    parse_mode='HTML')

    def send_phone_request(self, chat_id: int, text: str):
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(types.KeyboardButton(text='Отправить телефон', request_contact=True))

        self._bot.send_message(chat_id, text=text, reply_markup=markup, parse_mode='HTML')

    def send_message(self, chat_id: int, text: str,
                     inline_buttons: List[InlineViewButton] = None):
        markup = self.__get_markup(inline_buttons)
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
    bot_service.answer_callback(call.message.chat.id, call.from_user.id, callback_data=call.data)
    bot.answer_callback_query(call.id, text='')


@bot.message_handler(content_types=['contact'])
def contact(message: Message):
    if message.contact is not None:
        bot_service.answer_on_contacts(message.chat.id, message.from_user.id, message.contact.phone_number)
    else:
        pass


def start_telegram_bot():
    bot.polling(True)


start_telegram_bot()
