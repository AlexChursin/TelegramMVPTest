from fastapi.responses import JSONResponse
from fastapi import File, APIRouter
from fastapi.responses import JSONResponse
from pytrovich.enums import NamePart, Gender, Case
from pytrovich.maker import PetrovichDeclinationMaker
from .schemas import *
from routes.service import get_chat_id, create_cons
from telegram.aiogram_view import tg_view

message_route = APIRouter()


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


maker = PetrovichDeclinationMaker()



@message_route.get("/utils/petrovich", response_model=Petrovich)
async def utils(
        first_name: str = 'Елена',
        middle_name: str = 'Владимировна',
        last_name: str = 'Сидорова',
        case: Padej = Padej.GENITIVE,
        gender: MyGender = MyGender.FEMALE
):
    p_case = [Case(i) for i, p in enumerate(Padej) if case.name == p.name][0]
    p_gender = [Gender(i) for i, p in enumerate(MyGender) if gender.name == p.name][0]

    f = maker.make(NamePart.FIRSTNAME, p_gender, p_case, original_name=first_name)
    m = maker.make(NamePart.MIDDLENAME, p_gender, p_case, middle_name)
    l = maker.make(NamePart.LASTNAME, p_gender, p_case, last_name)
    return Petrovich(first_name=f, middle_name=m, last_name=l)
