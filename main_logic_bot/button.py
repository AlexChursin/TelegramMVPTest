from enum import Enum, auto

separator = '~'


class AutoName(Enum):
    def _generate_next_value_(self, start, count, last_values):
        return self


class ButtonCollection(AutoName):
    start_button = auto()
    start_emergency_button = auto()
    time_button = auto()
    back_main = auto()

    @staticmethod
    def from_callback(data: str) -> 'MyButton':
        return MyButton(*data.split(separator))


class MyButton:
    def __init__(self, label: str, data: str, type_value: str):
        self.label: str = label
        self.data: str = data
        self.__type_value: str = type_value

    @property
    def type(self):
        return ButtonCollection(self.__type_value)

    def to_callback(self) -> str:
        res = separator.join([d for d in self.__dict__.values()])
        return res
