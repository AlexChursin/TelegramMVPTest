from dataclasses import dataclass
from typing import Tuple, Union, Any, Optional, NoReturn

from backend_api import back_api
from messenger_api import mess_api
from .client_repo.client_entity import Consulate
from .utils import get_cons_token


async def _get_doctor_names(doc_token):
    doctor_name = await back_api.get_doctor_name(doc_token)
    if doctor_name is not None:
        doctor_name_p = await mess_api.get_petrovich(*doctor_name.split())
        return doctor_name, doctor_name_p


@dataclass
class ConsultationData:
    dialog_id: int
    doc_token: str
    patient_token: str
    is_emergency: bool
    client_name: str
    cons_token: str
    doctor_name: str


async def _get_doctor_from_url(url) -> Optional[ConsultationData]:
    cons_token = get_cons_token(url)
    if cons_token:
        dialog_id, doc_token, patient_token, is_emergency, client_name = await back_api.get_client_from_cons(cons_token)
        doctor_name = await back_api.get_doctor_name(doc_token)
        return ConsultationData(dialog_id, doc_token, patient_token, is_emergency, client_name, cons_token, doctor_name)
    return None
