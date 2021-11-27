from dataclasses import dataclass


@dataclass
class InlineViewButton:
    callback: str
    text: str

