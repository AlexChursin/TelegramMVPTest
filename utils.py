import re
from datetime import datetime
from typing import Optional

pattern = re.compile(r'((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))')


def is_number(text: str) -> bool:
    return pattern.match(text) is not None

def get_birthday(text: str) -> Optional[datetime]:
    try:
        return datetime.strptime(text, "%d.%m.%Y")
    except:
        return None