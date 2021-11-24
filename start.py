import logging
import telebot
import base64
import api
from telebot import types

from button_models import StartButton, TimeButton, get_button_from_callback
from entity import SendDataProvider, SendDataProvider
from urllib import parse
from text_config import text_config

KEY = '2109332410:AAFE3ADenKveU7w-zpP5pCYvJf2WwpC7sPc'
bot = telebot.TeleBot(KEY)


def get_refer(text) -> str | None:
    if " " in text:
        try:
            ref_str = text.split()[1]
            # pased = parse.unquote(ref_str).replace('+', ' ')
            return ref_str
        except:
            logging.warning(f'BAD REFERRAL URL: {text}')
            return None
    return None


@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    from_user = get_refer(message.text)
    text = text_config.start_text.format(str(from_user))
    SendDataProvider.set_user_obj(user_id, from_user)
    keyboard = [
        [types.InlineKeyboardButton(text=button.name,
                                    callback_data=StartButton(name=button.name, data=button.data).to_str())] for button
        in
        text_config.start_button_names
    ]
    markup = types.InlineKeyboardMarkup(keyboard)
    bot.send_message(message.chat.id, text=text, reply_markup=markup, parse_mode='HTML')


@bot.message_handler(commands=['info'])
def info_message(message):
    text = text_config.info_text
    bot.send_message(message.chat.id, text=text, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def inline(call):
    data = call.data
    user_id = call.from_user.id
    button_object = get_button_from_callback(data)
    if isinstance(button_object, StartButton):
        user = SendDataProvider.get_user_obj(user_id)
        if user is not None:
            user.start_button = button_object
            list_ = ['14:00', '17:15']
            keyboard = [
                [types.InlineKeyboardButton(text=value, callback_data=TimeButton(name=value, data=value).to_str())] for
                value in
                list_
            ]
            markup = types.InlineKeyboardMarkup(keyboard)
            bot.send_message(call.message.chat.id, text=text_config.cons_text, reply_markup=markup)
    if isinstance(button_object, TimeButton):
        user = SendDataProvider.get_user_obj(user_id)
        if user is not None:
            user.time_button = button_object
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            bot.register_next_step_handler(call.message, reason_petition)
            bot.send_message(user_id, text=text_config.reason_text)
    if isinstance(button_object, StartButton):
        pass

    # callback = Callback.parse(call.data)
    # text, markup = g_t_m(callback.display_id, callback.page)
    # bot.edit_message_text(chat_id=call.message.chat.id,
    #                       text=text,
    #                       message_id=call.message.message_id,
    #                       reply_markup=markup,
    #                       parse_mode='HTML')
    bot.answer_callback_query(call.id, text='')


def reason_petition(message):
    user_id = message.from_user.id
    text = message.text
    user = SendDataProvider.get_user_obj(user_id)
    if user is not None:
        user.reason_petition = text
        bot.send_message(message.chat.id, text=text_config.medications_text)
        bot.register_next_step_handler(message, medications_step)


def medications_step(message):
    user_id = message.from_user.id
    text = message.text
    user = SendDataProvider.get_user_obj(user_id)
    if user is not None:
        user.medications = text
        bot.send_message(message.chat.id, text=text_config.family_text)
        bot.register_next_step_handler(message, family_step)


def family_step(message):
    user_id = message.from_user.id
    text = message.text
    user = SendDataProvider.get_user_obj(user_id)
    if user is not None:
        user.family = text
        bot.send_message(message.chat.id, text=text_config.name_otch_text)
        bot.register_next_step_handler(message, name_otch_step)


def name_otch_step(message):
    user_id = message.from_user.id
    text = message.text
    user = SendDataProvider.get_user_obj(user_id)
    if user is not None:
        user.name_otch = text
        bot.send_message(message.chat.id, text=text_config.birthdate_text)
        bot.register_next_step_handler(message, birthday_step)


def birthday_step(message):
    user_id = message.from_user.id
    text = message.text
    user = SendDataProvider.get_user_obj(user_id)
    if user is not None:
        user.birthday = text
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)  # Подключаем клавиатуру
        button_phone = types.KeyboardButton(text="Отправить телефон",
                                            request_contact=True)  # Указываем название кнопки, которая появится у пользователя
        keyboard.add(button_phone)  # Добавляем эту кнопку
        bot.send_message(message.chat.id, text=text_config.get_number, reply_markup=keyboard)


@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        user_id = message.from_user.id
        phone_text = message.contact.phone_number
        user = SendDataProvider.get_user_obj(user_id)
        if user is not None:
            user.number = phone_text
            send_text = text_config.finish.format(user.start_button.name.lower(), user.time_button.name.lower())
            keyboard = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, text=send_text, reply_markup=keyboard)
            bot.send_message(message.chat.id, text=f'Данные для отправки: \n {user}', reply_markup=keyboard)
            api.send_dialog(send_user=user)


def start_telegram_bot():
    bot.polling(True)


start_telegram_bot()
