import re
from typing import Optional

pattern = re.compile(
    r'((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))')


def is_number(text: str) -> bool:
    return pattern.match(text) is not None


def fix_number(text: str) -> str:
    if text.startswith('7'):
        text = '+' + text
    elif text.startswith('8'):
        text = '+7' + text[1:]
    return text


def is_first_middle_name(text: str) -> bool:
    try:
        first = text.split()[0]
        middle = text.split()[1]
        if len(first) > 3 and len(middle) > 3:
            return True
    except:
        pass
    return False


def get_birthday(text: str) -> Optional[str]:
    try:
        int_v = int(text)
        if 5 < int_v < 120:
            return str(int_v)
    except:
        return None
    return None
