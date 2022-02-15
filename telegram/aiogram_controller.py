import json
import threading

from aiogram.types import Message, CallbackQuery
from aiogram.utils import executor
from sentry_sdk import capture_exception
from .bot_init import bot, dp
from .main_logic_bot.config.text_config import TextBot
from .main_logic_bot.service_provider import bot_service


def get_config_from_file():
    return TextBot(**json.load(
        open('telegram/main_logic_bot/config/bot_text_word.json', 'r', encoding='UTF-8')))




@dp.message_handler(commands=['start'])
async def on_start_command(message: Message):
    try:
        await bot_service.answer_on_start_command(chat_id=message.chat.id, user_id=message.from_user.id,
                                                  refer_url_text=message.text,
                                                  username=message.from_user.username,
                                                  firstname=message.from_user.username,
                                                  lastname=message.from_user.username)


    except Exception as e:
        capture_exception(e)


@dp.message_handler(commands=['help'])
async def info_message(message):
    await bot_service.send_help(chat_id=message.chat.id)



@dp.message_handler(commands=['recommend'])
async def info_message(message):
    await bot_service.send_recommend(user_id=message.from_user.id, chat_id=message.chat.id)


@dp.message_handler(content_types=['photo'])
async def photo_image(message: Message):
    try:
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        result = await bot.download_file(file.file_path)
        await bot_service.send_file_to_doctor(user_id=message.from_user.id, filename=file.file_path, bytes_oi=result)
    except Exception as e:
        capture_exception(e)



@dp.message_handler(content_types=['document'])
async def photo_document(message: Message):
    try:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        result = await bot.download_file(file.file_path)
        await bot_service.send_file_to_doctor(user_id=message.from_user.id, filename=message.document.file_name, bytes_oi=result)

    except Exception as e:
        capture_exception(e)


@dp.message_handler(commands=['reset'])
async def info_message(message):
    await bot_service.reset_user(chat_id=message.chat.id, user_id=message.from_user.id)


@dp.message_handler()
async def text_message(message: Message):
    try:
        await bot_service.answer_on_any_message(chat_id=message.chat.id, user_id=message.from_user.id,
                                                text=message.text)
    except Exception as e:
        capture_exception(e)


@dp.callback_query_handler()
async def inline(call: CallbackQuery):
    try:
        await bot_service.answer_callback(chat_id=call.message.chat.id,
                                          user_id=call.from_user.id, callback_data=call.data)
        await bot.answer_callback_query(call.id, text='')
    except Exception as e:
        capture_exception(e)

#
# @dp.message_handler(content_types=['contact'])
# async def contact(message: Message):
#     # try:
#     if message.contact is not None:
#         await bot_service.answer_on_contacts(message.chat.id, message.from_user.id, message.contact.phone_number)
#     else:
#         pass


# except Exception as e:
#     capture_exception(e)


def start_telegram_bot():
    executor.start_polling(dp, skip_updates=True)


def start_telegram_bot_in_new_thread():
    threading.Thread(target=start_telegram_bot).start()
