import json
from typing import List
from telebot.types import Message, CallbackQuery
from telebot import types, TeleBot
from main_logic_bot.bot_entity import InlineViewButton, ReplyViewButton
from main_logic_bot.bot_interface import IView
from main_logic_bot.service import BotService
from config.text_config import TextBot

KEY = '2110497364:AAFR0osj2TGrLHbcTrxkN6CGDWBY1tVA9Ao'
bot: TeleBot = TeleBot(KEY)


class TelegramView(IView):
    def __init__(self):
        self._bot: TeleBot = bot

    def send_message(self, chat_id: int, text: str,
                     inline_buttons: List[InlineViewButton] = None,
                     reply_buttons: List[ReplyViewButton] = None):
        markup = types.ReplyKeyboardRemove()
        if inline_buttons is not None:
            markup = types.InlineKeyboardMarkup()
            for button in inline_buttons:
                markup.add(types.InlineKeyboardButton(text=button.text, callback_data=button.callback, ))

        if reply_buttons is not None:
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            for button in reply_buttons:
                markup.add(types.KeyboardButton(text=button.text, request_contact=button.request_contact))

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
