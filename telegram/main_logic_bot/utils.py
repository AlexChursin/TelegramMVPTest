import logging
from typing import Optional


def get_cons_token(text) -> Optional[str]:
    if ' ' in text:
        try:
            ref_str = text.split(' ')[1]
            if len(ref_str) > 15:
                return ref_str
        except IndexError:
            logging.warning(f'BAD REFERRAL URL: {text}')
    return None
