from hashlib import sha256


def get_hash(plain_text: str) -> str:
    return sha256(plain_text.encode('utf-8')).hexdigest()
