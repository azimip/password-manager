import re
from utils import const


def is_strong(new_password: str) -> bool:
    return (
        len(new_password) >= const.PASSWORD_MINIMUM_LENGTH and
        bool(re.search(r'\d', new_password)) and
        bool(set(const.SPECIAL_CHARS).intersection(set(new_password)))
    )
