import dataclasses
import logging
from enum import auto, Enum
from typing import Optional, Tuple, Union
from dataclasses import dataclass


@dataclass
class DoctorResult:
    token: str


@dataclass
class ConsResult:
    token: str


def get_refer(text) -> Optional[Union[DoctorResult, ConsResult]]:
    if ' ' in text:
        try:
            ref_str = text.split(' ')[1]
            if len(ref_str) > 15:
                if ref_str.startswith('doc_'):
                    return DoctorResult(ref_str[4:])
                if ref_str.startswith('cons_'):
                    return ConsResult(ref_str[5:])
            return None
        except IndexError:
            logging.warning(f'BAD REFERRAL URL: {text}')
    return None
