import re
from datetime import datetime
from typing import Optional

pattern = re.compile(r'((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))')


def is_number(text: str) -> bool:
    return pattern.match(text) is not None

def get_birthday(text: str) -> Optional[str]:
    try:
        int_v = int(text)
        if 5 < int_v < 120:
            return str(int_v)
    except:
        return None
    return None
