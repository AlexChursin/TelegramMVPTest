from typing import Optional

import uvicorn
from fastapi import FastAPI, File
from pydantic import BaseModel

from telegram_view import tg_view

app = FastAPI()


class Message(BaseModel):
    text: str
    price: float
    is_offer: Optional[bool] = None


@app.post("/send/text_message")
def read_item(cons_id: int, text: str):
    chat_id = 1
    tg_view.send_message(chat_id, text)
    return {"item_id": cons_id, "text": text}


@app.post("/send/file_message")
def read_item(cons_id: int, filename: str, body: bytes = File(...)):
    chat_id = 1
    tg_view.send_file(chat_id, data=body, filename=filename)
    return {"item_id": cons_id, "len": len(body)}


uvicorn.run(app, host="0.0.0.0", port=8000)
