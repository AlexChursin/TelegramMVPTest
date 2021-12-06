from typing import List, Optional

from telegram.main_logic_bot.consultate_client_data.client_entity import StartClientData


def get_doctor_from_refer(value: str = None):
    if value is not None:
        return "Елены Петровой"
    else:
        return None


def create_dialog(send_user: StartClientData) -> Optional[int]:
    """

    :rtype: object
    """
    return 1


def get_list_free_times() -> List[str]:
    return ['14:00', '17:15']


def send_patient_text_message(text:str, dialog_id: int):
    return True