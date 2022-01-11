from enum import Enum, auto


class State(Enum):
    start_first = auto()
    await_reason_petition_text = auto()
    await_name_otch_text = auto()
    await_contacts = auto()
    dialog = auto()

    def __str__(self):
        return str(self.value)
