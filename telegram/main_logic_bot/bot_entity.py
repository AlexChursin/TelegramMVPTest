from dataclasses import dataclass
from typing import Optional


@dataclass
class InlineViewButton:
    callback: str
    text: str
    url: Optional[str] = None



@dataclass
class ViewButton:
    text: str



@dataclass
class Schedule:
    id: int
    time: str

