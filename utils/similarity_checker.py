from abc import ABC, abstractmethod
from typing import List

from utils.hash import get_hash


class SimilarityVisitor(ABC):
    def __init__(self, new_password: str, old_passowrd_hashes: List[str]):
        self.new_password = new_password
        self.old_passowrd_hashes = old_passowrd_hashes

    @abstractmethod
    def is_similar(self) -> bool:
        pass

class ReversedVisitor(SimilarityVisitor):
    def is_similar(self) -> bool:
        password_hash = get_hash(plain_text=self.new_password)
        return password_hash in self.old_passowrd_hashes

class PowersetVisitor(SimilarityVisitor):
    def get_powerset(self, string: str) -> List[str]:
        result = [""]
        for ch1 in string:
            result += [ch2 + ch1 for ch2 in result]

        return result

    def is_similar(self) -> bool:
        password_hashes = [get_hash(e) for e in self.get_powerset(self.new_password)]
        return True if set(password_hashes).intersection(self.old_passowrd_hashes) else False

SIMIARITY_VISITORS = [
    ReversedVisitor,
    PowersetVisitor,
]

def is_similar(new_password: str, old_passowrd_hashes: List[str]) -> bool:
    for visitor_class in SIMIARITY_VISITORS:
        if visitor_class(new_password=new_password, old_passowrd_hashes=old_passowrd_hashes).is_similar():
            return True

    return False
