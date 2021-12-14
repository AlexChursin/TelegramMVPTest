from fastapi import File, APIRouter
from fastapi.responses import JSONResponse
from pytrovich.maker import PetrovichDeclinationMaker

from messenger_api import mess_api
from .schemas import *
from telegram.aiogram_view import tg_view

message_route = APIRouter()
util_route = APIRouter()


@message_route.post("/send/text_message", response_model=Message, responses={404: {"model": ErrorMessage}})
async def text(dialog_id: int, text: str, doctor_name: str):
    chat_id = await mess_api.get_chat_id(dialog_id)
    if chat_id is not None:
        await tg_view.send_message_doctor(chat_id, text, doctor_name)
        return Message(chat_id=chat_id)
    else:
        return JSONResponse(status_code=404, content={'detail': 'Consulate not found'})


@message_route.post("/command/create_consulate", deprecated=True)
async def create(dialog_id: int, chat_id: int):
    id_ = await mess_api.create_cons(chat_id, dialog_id)
    await tg_view.send_message(chat_id, 'создана запись с консультацией')
    return {"id": id_, }


@message_route.post("/send/file_message", response_model=Message, responses={404: {"model": ErrorMessage}})
async def file(dialog_id: int, filename: str, doctor_name: str, body: bytes = File(...)):
    chat_id = mess_api.get_chat_id(dialog_id=dialog_id)
    if chat_id is not None:
        await tg_view.send_file_from_doctor(chat_id, data=body, filename=filename, doctor_name=doctor_name)
        return Message(chat_id=chat_id)
    else:
        return JSONResponse(status_code=404, content={'detail': 'Consulate not found'})


maker = PetrovichDeclinationMaker()


