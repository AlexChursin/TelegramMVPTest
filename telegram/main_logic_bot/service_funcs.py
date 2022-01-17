from typing import Tuple, Union, Any, Optional, NoReturn

from backend_api import back_api
from messenger_api import mess_api
from .client_repo.client_entity import Consulate
from .utils import get_refer, DoctorResult, ConsResult


async def _get_doctor_names(doc_token):
    doctor_name = await back_api.get_doctor_name(doc_token)
    if doctor_name is not None:
        doctor_name_p = await mess_api.get_petrovich(*doctor_name.split())
        return doctor_name, doctor_name_p


async def _get_doctor_from_url(url) -> Tuple[Any, Union[DoctorResult, ConsResult, NoReturn]]:
    result = get_refer(url)
    if type(result) is DoctorResult:
        names = await _get_doctor_names(result.token)
        if names:
            doctor_name, doctor_name_p = names
            return (doctor_name, doctor_name_p), result
    if type(result) is ConsResult:
        dialog_id, doc_token, patient_token, is_emergency, name = await back_api.get_client_from_cons(result.token)
        names = _get_doctor_names(doc_token)
        if names:
            return (dialog_id, doc_token, patient_token, is_emergency, name, *names), result
    return None, None
