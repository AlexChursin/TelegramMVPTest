import logging
from enum import auto, Enum
from typing import Optional, Tuple


class TokenResult(Enum):
    doctor = auto()
    consulate = auto()
    none = auto()


def get_refer(text) -> Tuple[TokenResult, Optional[str]]:
    if ' ' in text:
        try:
            ref_str = text.split(' ')[1]
            if len(ref_str) > 15:
                if ref_str.startswith('doc_'):
                    return TokenResult.doctor, ref_str[4:]
                if ref_str.startswith('cons_'):
                    return TokenResult.consulate, ref_str[5:]
            return TokenResult.none, None
        except IndexError:
            logging.warning(f'BAD REFERRAL URL: {text}')
    return TokenResult.none, None
