from typing import Optional

from fastapi import File, APIRouter, Query, UploadFile
from fastapi.responses import JSONResponse

from messenger_api import mess_api
from telegram.main_logic_bot.service_provider import bot_service
from .schemas import *

message_route = APIRouter()


class DialogMessage(BaseModel):
    dialog_id: int
    text: str
    doctor_name: str


class FinishMessage(BaseModel):
    dialog_id: int
    text: str
    doctor_name: Optional[str] = Query(None, description='Имя доктора в падеже. Если добавить это поле, то сообщение будет отправлено от имени ассистента')


@message_route.post("/send/text_message", response_model=Message, responses={404: {"model": ErrorMessage}})
async def text_message(dialog_message: DialogMessage):
    consulate = await mess_api.get_consulate(dialog_message.dialog_id)
    if consulate is not None:
        await bot_service.send_message_doctor(chat_id=consulate.chat_id, text=dialog_message.text, doctor_name=dialog_message.doctor_name)
        return Message(chat_id=consulate.chat_id)
    else:
        return JSONResponse(status_code=404, content={'detail': 'Consulate not found'})


@message_route.post("/send/finish_message", response_model=Message, responses={404: {"model": ErrorMessage}})
async def finish_message(dialog_message: FinishMessage):
    consulate = await mess_api.get_consulate(dialog_message.dialog_id)
    if consulate:
        if consulate.chat_id is not None:
            chat_id = await bot_service.finish_consulate(dialog_message.dialog_id, dialog_message.text, dialog_message.doctor_name)
            if chat_id:
                return Message(chat_id=chat_id)
    return JSONResponse(status_code=404, content={'detail': 'Consulate not found'})


@message_route.post("/send/file_message", response_model=Message, responses={404: {"model": ErrorMessage}})
async def file_message(dialog_id: int, doctor_name: str, file: UploadFile = File(...)):
    consulate = await mess_api.get_consulate(dialog_id)

    if consulate is not None:
        await bot_service.send_file_from_doctor(consulate.chat_id, data=await file.read(), filename=file.filename, doctor_name=doctor_name)
        return Message(chat_id=consulate.chat_id)
    else:
        return JSONResponse(status_code=404, content={'detail': 'Consulate not found'})


