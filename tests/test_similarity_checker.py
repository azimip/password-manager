import unittest

from utils.hash import get_hash
from utils.similarity_checker import is_similar


class TestSimilarityChecker(unittest.TestCase):
    def test_reversed(self):
        password = "crypto123"
        hash_val = get_hash(password[::-1])
        self.assertEqual(is_similar(new_password=password, old_passowrd_hashes=[hash_val]), True)

    def test_powerset(self):
        password = "crypto123"
        hash_val = get_hash("crpto12")
        self.assertEqual(is_similar(new_password=password, old_passowrd_hashes=[hash_val]), True)

    def test_add_on(self):
        password = "crypto123"
        hash_val = get_hash("crypto@123")
        self.assertEqual(is_similar(new_password=password, old_passowrd_hashes=[hash_val]), True)

    def test_permutation(self):
        password = "crypto-CRYPTO_123@"
        hash_val = get_hash("crypto_CRYPTO@123-")
        self.assertEqual(is_similar(new_password=password, old_passowrd_hashes=[hash_val]), True)