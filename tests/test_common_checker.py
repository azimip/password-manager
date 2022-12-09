import unittest

from utils.hash import get_hash
from utils.common_checker import is_common


class TestSimilarityChecker(unittest.TestCase):
    def test_reversed(self):
        password = "password"
        self.assertEqual(is_common(new_password=password), True)
