import re

pattern = re.compile(r'^(?:\+?44)?[07]\d{9,13}$')


def is_number(text: str) -> bool:
    return pattern.match(text) is not None
