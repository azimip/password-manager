from utils import const


def is_common(new_password: str) -> bool:
    return new_password in const.COMMON_PASSWORDS
