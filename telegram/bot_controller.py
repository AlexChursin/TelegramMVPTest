import json
import threading

from aiogram.types import Message, CallbackQuery
from aiogram.utils import executor

from .bot_init import bot, dp

from .main_logic_bot.config.text_config import TextBot
from .main_logic_bot.service import BotService
from .aiogram_view import tg_view

bot_service = BotService(view=tg_view,
                         text_config=TextBot(**json.load(open('telegram/main_logic_bot/config/bot_text_word.json', 'r', encoding='UTF-8'))))


@dp.message_handler(commands=['start'])
async def on_start_command(message: Message):
    await bot_service.send_start_message(chat_id=message.chat.id, user_id=message.from_user.id,
                                         refer_url_text=message.text)


@dp.message_handler(commands=['info'])
async def info_message(message):
    await bot_service.send_info(chat_id=message.chat.id)


@dp.message_handler(commands=['reset'])
async def info_message(message):
    await bot_service.reset_user(user_id=message.from_user.id)


@dp.message_handler()
async def text_message(message: Message):
    await bot_service.answer_on_any_message(chat_id=message.chat.id, user_id=message.from_user.id, text=message.text)


@dp.callback_query_handler()
async def inline(call: CallbackQuery):
    await bot_service.answer_callback(chat_id=call.message.chat.id,
                                      bot_message_id=call.message.message_id,
                                      user_id=call.from_user.id, callback_data=call.data)
    await bot.answer_callback_query(call.id, text='')


@dp.message_handler(content_types=['contact'])
async def contact(message: Message):
    if message.contact is not None:
        await bot_service.answer_on_contacts(message.chat.id, message.from_user.id, message.contact.phone_number)
    else:
        pass


def start_telegram_bot():
    executor.start_polling(dp, skip_updates=True)


def start_telegram_bot_in_new_thread():
    threading.Thread(target=start_telegram_bot).start()

