from aiogram import Bot, Dispatcher
from telegram.config import TELEGRAM_TOKEN

bot: Bot = Bot(token=TELEGRAM_TOKEN)
dp: Dispatcher = Dispatcher(bot)
