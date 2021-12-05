import os
from typing import Optional

import uvicorn
from loguru import logger
from aiogram.types import Update
from fastapi import FastAPI, File
from pydantic import BaseModel

from telegram.bot_controller import bot, dp
from db.core import database, engine, metadata
from route.service import get_chat_id, create_cons
from telegram.bot_init import KEY
from telegram.telegram_view import tg_view

app = FastAPI()
WEBHOOK_PATH = f"/bot/{KEY}"
WEBHOOK_URL = os.environ.get('URL_SERVER_WEBHOOK') + WEBHOOK_PATH


@app.on_event("startup")
async def startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )
    logger.info(f'telegram webhook url: {webhook_info.url}')

    metadata.create_all(engine)
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


class Message(BaseModel):
    text: str
    price: float
    is_offer: Optional[bool] = None


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    tg_update = Update(**update)
    await dp.process_update(tg_update)


@app.post("/send/text_message")
async def text(cons_id: int, text: str):
    chat_id = get_chat_id(cons_id)
    await tg_view.send_message(chat_id, text)
    return {"chat_id": chat_id, "text": text}


@app.post("/command/text_message", tags=['COM'])
async def create(cons_id: int, chat_id: int):
    id_ = await create_cons(chat_id, cons_id)
    await tg_view.send_message(chat_id, 'создана запись с консультацией')
    return {"id": id_, }


@app.post("/send/file_message")
async def file(cons_id: int, filename: str, body: bytes = File(...)):
    chat_id = get_chat_id(cons_id=cons_id)
    await tg_view.send_file(chat_id, data=body, filename=filename)
    return {"chat_id": chat_id, "len": len(body)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)