from enum import Enum, auto


class State(Enum):
    start_first = auto()
    start_second = auto()
    await_reason_petition_text = auto()
    await_medication_text = auto()
    await_family_text = auto()
    await_name_otch_text = auto()
    await_birthday_text = auto()
    await_contacts = auto()
    finish = auto()

    def __str__(self):
        return str(self.value)
