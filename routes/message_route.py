import os
from http import HTTPStatus
from typing import Optional

import uvicorn
from loguru import logger
from aiogram.types import Update
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, HTTPException, APIRouter
from pydantic import BaseModel, Field

from telegram.bot_controller import bot, dp
from db.core import database, engine, metadata
from routes.service import get_chat_id, create_cons
from telegram.bot_init import KEY
from telegram.aiogram_view import tg_view

message_route = APIRouter()


class ErrorMessage(BaseModel):
    detail: str


class Message(BaseModel):
    chat_id: int = Field(1, description='чат привязанный к консультации')



@message_route.post("/send/text_message", response_model=Message, responses={404: {"model": ErrorMessage}})
async def text(cons_id: int, text: str, doctor_name: str):
    chat_id = await get_chat_id(cons_id)
    if chat_id is not None:
        await tg_view.send_message_doctor(chat_id, text, doctor_name)
        return Message(chat_id=chat_id)
    else:
        return JSONResponse(status_code=404, content={'detail': 'Consulate not found'})


@message_route.post("/command/create_consulate", deprecated=True)
async def create(cons_id: int, chat_id: int):
    id_ = await create_cons(chat_id, cons_id)
    await tg_view.send_message(chat_id, 'создана запись с консультацией')
    return {"id": id_, }


@message_route.post("/send/file_message", response_model=Message, responses={404: {"model": ErrorMessage}})
async def file(cons_id: int, filename: str, doctor_name: str, body: bytes = File(...)):
    chat_id = get_chat_id(cons_id=cons_id)
    if chat_id is not None:
        await tg_view.send_file_from_doctor(chat_id, data=body, filename=filename, doctor_name=doctor_name)
        return Message(chat_id=chat_id)
    else:
        return JSONResponse(status_code=404, content={'detail': 'Consulate not found'})

