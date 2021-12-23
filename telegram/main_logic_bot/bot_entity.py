from dataclasses import dataclass
from typing import Optional


@dataclass
class InlineViewButton:
    callback: str
    text: str


@dataclass
class ViewButton:
    text: str



@dataclass
class Schedule:
    id: int
    time: str

