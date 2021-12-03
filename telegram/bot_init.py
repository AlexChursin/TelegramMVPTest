import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
load_dotenv()
KEY = os.environ.get('TELEGRAM_TOKEN')
bot: Bot = Bot(token=KEY)
dp: Dispatcher = Dispatcher(bot)
