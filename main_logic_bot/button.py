from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

separator = '~!'


class ButtonTypes(Enum):
    start_button = 'start_button'
    time_button = 'time_button'


class MyButton(ABC):
    name: str
    data: str

    @abstractmethod
    def to_str(self) -> str: ...


def get_button_from_callback(data: str) -> MyButton:
    spl = data.split(separator)
    key = spl[0]
    if ButtonTypes(key) is ButtonTypes.start_button:
        return StartButton.get_from_callback(spl[1:])
    if ButtonTypes(key) is ButtonTypes.time_button:
        return TimeButton.get_from_callback(spl[1:])


def get_callback(button_type: ButtonTypes, button: MyButton) -> str:
    v = [d for d in button.__dict__.values()]
    return separator.join([button_type.value] + v)


@dataclass
class StartButton(MyButton):
    name: str
    data: str

    def to_str(self) -> str:
        res = get_callback(ButtonTypes.start_button, self)
        return res

    @staticmethod
    def get_from_callback(list_arg: list) -> 'StartButton':
        return StartButton(*list_arg)


@dataclass
class TimeButton(MyButton):
    name: str
    data: str

    def to_str(self) -> str:
        res = get_callback(ButtonTypes.time_button, self)
        return res

    @staticmethod
    def get_from_callback(list_arg: list) -> 'TimeButton':
        return TimeButton(*list_arg)



