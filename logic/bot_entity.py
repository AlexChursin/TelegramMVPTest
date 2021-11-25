from dataclasses import dataclass


@dataclass
class InlineViewButton:
    callback: str
    text: str


@dataclass
class ReplyViewButton:
    text: str
    request_contact: bool = False
