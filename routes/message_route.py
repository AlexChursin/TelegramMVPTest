from typing import Optional

from fastapi import File, APIRouter, Query
from fastapi.responses import JSONResponse
from pytrovich.maker import PetrovichDeclinationMaker

from messenger_api import mess_api
from .schemas import *
from telegram.aiogram_view import tg_view
from .service import finish_consulate

message_route = APIRouter()
util_route = APIRouter()


@message_route.post("/send/text_message", response_model=Message, responses={404: {"model": ErrorMessage}})
async def text_message(dialog_id: int, text: str, doctor_name: str):
    consulate = await mess_api.get_consulate(dialog_id)
    if consulate is not None:
        await tg_view.send_message_doctor(chat_id=consulate.chat_id, text=text, doctor_name=doctor_name)
        return Message(chat_id=consulate.chat_id)
    else:
        return JSONResponse(status_code=404, content={'detail': 'Consulate not found'})


@message_route.post("/send/finish_message", response_model=Message, responses={404: {"model": ErrorMessage}})
async def finish_message(dialog_id: int, text: str, doctor_name: Optional[str] = Query(None, description='Имя доктора. Если добавить это поле, то сообщение будет отправлено от имени ассистента')):
    chat_id = await finish_consulate(dialog_id, text, doctor_name)
    if chat_id:
        return Message(chat_id=chat_id)
    else:
        return JSONResponse(status_code=404, content={'detail': 'Consulate not found'})


@message_route.post("/command/create_consulate", deprecated=True)
async def create_consulate(dialog_id: int, chat_id: int):
    id_ = await mess_api.set_client(chat_id, dialog_id)
    await tg_view.send_assistant_message(chat_id, 'создана запись с консультацией')
    return {"id": id_, }


@message_route.post("/send/file_message", response_model=Message, responses={404: {"model": ErrorMessage}})
async def file_message(dialog_id: int, filename: str, doctor_name: str, body: bytes = File(...)):
    chat_id = mess_api.get_chat_id(dialog_id=dialog_id)
    if chat_id is not None:
        await tg_view.send_file_from_doctor(chat_id, data=body, filename=filename, doctor_name=doctor_name)
        return Message(chat_id=chat_id)
    else:
        return JSONResponse(status_code=404, content={'detail': 'Consulate not found'})


maker = PetrovichDeclinationMaker()


