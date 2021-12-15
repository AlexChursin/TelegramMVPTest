from dataclasses import dataclass


@dataclass
class InlineViewButton:
    callback: str
    text: str




@dataclass
class Schedule:
    id: int
    time: str

