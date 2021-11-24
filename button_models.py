from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

separator = '~!'


class Field(Enum):
    start_button = 'start_button'
    time_button = 'time_button'


class MyButton(ABC):

    @abstractmethod
    def to_str(self) -> str: ...


def get_button_from_callback(data: str) -> MyButton:
    spl = data.split(separator)
    key = spl[0]
    if Field(key) is Field.start_button:
        return StartButton.from_callback(spl[1:])
    if Field(key) is Field.time_button:
        return TimeButton.from_callback(spl[1:])


def get_callback(key: Field, button: MyButton) -> str:
    v = [d for d in button.__dict__.values()]
    return separator.join([key.value] + v)


@dataclass
class StartButton(MyButton):
    name: str
    data: str

    def to_str(self) -> str:
        res = get_callback(Field.start_button, self)
        return res

    @staticmethod
    def from_callback(list_arg: list) -> 'StartButton':
        return StartButton(*list_arg)


@dataclass
class TimeButton(MyButton):
    name: str
    data: str

    def to_str(self) -> str:
        res = get_callback(Field.time_button, self)
        return res

    @staticmethod
    def from_callback(list_arg: list) -> 'TimeButton':
        return TimeButton(*list_arg)



