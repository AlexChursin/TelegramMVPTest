from typing import Optional

import uvicorn
from fastapi import FastAPI, File
from pydantic import BaseModel

from route.service import get_chat_id
from telegram_view import tg_view

app = FastAPI()


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


class Message(BaseModel):
    text: str
    price: float
    is_offer: Optional[bool] = None


@app.post("/send/text_message")
async def read_item(cons_id: int, text: str):
    chat_id = get_chat_id(cons_id)
    await tg_view.send_message(chat_id, text)
    return {"chat_id": chat_id, "text": text}


@app.post("/send/file_message")
async def read_item(cons_id: int, filename: str, body: bytes = File(...)):
    chat_id = get_chat_id(cons_id=cons_id)
    await tg_view.send_file(chat_id, data=body, filename=filename)
    return {"chat_id": chat_id, "len": len(body)}


uvicorn.run(app, host="0.0.0.0", port=8000)
