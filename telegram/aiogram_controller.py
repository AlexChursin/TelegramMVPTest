import json
import threading

from aiogram.types import Message, CallbackQuery
from aiogram.utils import executor
from sentry_sdk import capture_exception, capture_message

from .bot_init import bot, dp
from .main_logic_bot.client_repo.client_provider import MemoryClientRepo

from .main_logic_bot.config.text_config import TextBot
from .main_logic_bot.service import BotService
from .aiogram_view import tg_view

bot_service = BotService(view=tg_view,
                         text_config=TextBot(**json.load(open('telegram/main_logic_bot/config/bot_text_word.json', 'r', encoding='UTF-8'))),
                         client_repo=MemoryClientRepo())


@dp.message_handler(commands=['start'])
async def on_start_command(message: Message):
    try:
        await bot_service.send_start_message(chat_id=message.chat.id, user_id=message.from_user.id,
                                             refer_url_text=message.text)
    except Exception as e:
        capture_exception(e)


@dp.message_handler(commands=['info'])
async def info_message(message):
    await bot_service.send_info(chat_id=message.chat.id)


@dp.message_handler(commands=['reset'])
async def info_message(message):
    await bot_service.reset_user(chat_id=message.chat.id, user_id=message.from_user.id)


@dp.message_handler(commands=['contact'])
async def send_contact(message):
    await bot.send_contact(message.chat.id, phone_number='123', first_name='Имя', last_name='Фамилия', vcard=
    "BEGIN:VCARD\n" +
    "VERSION:3.0\n" +
    "N:Solo;Han\n" +
    "ORG:Организация ассистент\n" +
    "URL:https://t.me/docCRMbot?start=doc_012e752d-d779-40c6-8c97-e470c1dfc175\n"
    "TEL;TYPE=voice,work,pref:+1234567890\n" +
    "EMAIL:hansolo@mfalcon.com\n" +
    "END:VCARD")


@dp.message_handler()
async def text_message(message: Message):
    try:
        await bot_service.answer_on_any_message(chat_id=message.chat.id, user_id=message.from_user.id, text=message.text)
    except Exception as e:
        capture_exception(e)

@dp.callback_query_handler()
async def inline(call: CallbackQuery):
    try:
        await bot_service.answer_callback(chat_id=call.message.chat.id,
                                          bot_message_id=call.message.message_id,
                                          user_id=call.from_user.id, callback_data=call.data)
        await bot.answer_callback_query(call.id, text='')
    except Exception as e:
        capture_exception(e)


@dp.message_handler(content_types=['contact'])
async def contact(message: Message):
    try:
        if message.contact is not None:
            await bot_service.answer_on_contacts(message.chat.id, message.from_user.id, message.contact.phone_number)
        else:
            pass
    except Exception as e:
        capture_exception(e)


def start_telegram_bot():
    executor.start_polling(dp, skip_updates=True)


def start_telegram_bot_in_new_thread():
    threading.Thread(target=start_telegram_bot).start()

