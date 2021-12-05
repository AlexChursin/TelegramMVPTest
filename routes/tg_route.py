import os

from aiogram.types import Update
from fastapi import APIRouter
from loguru import logger

from telegram.bot_controller import bot, dp
from telegram.bot_init import KEY

WEBHOOK_PATH = f"/bot/{KEY}"
WEBHOOK_URL = os.environ.get('URL_SERVER_WEBHOOK') + WEBHOOK_PATH

tg_route = APIRouter()


async def set_webhook() -> str:
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )
    webhook_info = await bot.get_webhook_info()
    logger.info(f'telegram webhook url: {webhook_info.url}')
    return webhook_info.url


@tg_route.post(WEBHOOK_PATH, include_in_schema=False)
async def bot_webhook(update: dict):
    tg_update = Update(**update)
    await dp.process_update(tg_update)
