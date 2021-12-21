
from backend_api import back_api
from messenger_api import mess_api
from .utils import get_refer, TokenResult


async def _get_doctor_from_url(url):
    doctor_name, doctor_name_p, token = None, None, None
    result, token = get_refer(url)
    if result is TokenResult.doctor:
        doctor_name = await back_api.get_doctor_name(token)
        if doctor_name is not None:
            doctor_name_p = await mess_api.get_petrovich(*doctor_name.split())
    return doctor_name, doctor_name_p, token


async def _send_sorry_mess(token: str):
    doctor_name = await back_api.get_doctor_name(token)
    if doctor_name is not None:
        return await mess_api.get_petrovich(*doctor_name.split())
    return None
