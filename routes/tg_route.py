import os

from aiogram.types import Update
from fastapi import APIRouter
from loguru import logger

from telegram.bot_controller import bot, dp
from telegram.bot_init import TELEGRAM_TOKEN
from telegram.config import URL_SERVER, SERVER_PREFIX

WEBHOOK_PATH = f"/bot/{TELEGRAM_TOKEN}"
WEBHOOK_URL = URL_SERVER + SERVER_PREFIX + WEBHOOK_PATH

tg_route = APIRouter()


async def set_webhook() -> str:
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )
    webhook_info = await bot.get_webhook_info()
    return webhook_info.url


@tg_route.post(WEBHOOK_PATH, include_in_schema=False)
async def bot_webhook(update: dict):
    tg_update = Update(**update)
    await dp.process_update(tg_update)
