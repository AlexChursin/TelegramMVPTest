from typing import Optional

from fastapi import File, APIRouter, Query
from fastapi.responses import JSONResponse

from messenger_api import mess_api
from telegram.aiogram_view import tg_view
from .schemas import *
from .service import finish_consulate

message_route = APIRouter()
util_route = APIRouter()


class DialogMessage(BaseModel):
    dialog_id: int
    text: str
    doctor_name: str


class DialogFile(BaseModel):
    dialog_id: int
    filename: str
    doctor_name: str
    body: bytes = File(...)


class FinishMessage(BaseModel):
    dialog_id: int
    text: str
    doctor_name: Optional[str] = Query(None, description='Имя доктора в падеже. Если добавить это поле, то сообщение будет отправлено от имени ассистента')


@message_route.post("/send/text_message", response_model=Message, responses={404: {"model": ErrorMessage}})
async def text_message(dialog_message: DialogMessage):
    consulate = await mess_api.get_consulate(dialog_message.dialog_id)
    if consulate is not None:
        await tg_view.send_message_doctor(chat_id=consulate.chat_id, text=dialog_message.text, doctor_name=dialog_message.doctor_name)
        return Message(chat_id=consulate.chat_id)
    else:
        return JSONResponse(status_code=404, content={'detail': 'Consulate not found'})


@message_route.post("/send/finish_message", response_model=Message, responses={404: {"model": ErrorMessage}})
async def finish_message(dialog_message: FinishMessage):
    chat_id = await finish_consulate(dialog_message.dialog_id, dialog_message.text, dialog_message.doctor_name)
    if chat_id:
        return Message(chat_id=chat_id)
    else:
        return JSONResponse(status_code=404, content={'detail': 'Consulate not found'})


@message_route.post("/send/file_message", response_model=Message, responses={404: {"model": ErrorMessage}})
async def file_message(dialog_file: DialogFile):
    consulate = await mess_api.get_consulate(dialog_file.dialog_id)
    if consulate is not None:
        await tg_view.send_file_from_doctor(consulate.chat_id, data=dialog_file.body, filename=dialog_file.filename, doctor_name=dialog_file.doctor_name)
        return Message(chat_id=consulate.chat_id)
    else:
        return JSONResponse(status_code=404, content={'detail': 'Consulate not found'})


