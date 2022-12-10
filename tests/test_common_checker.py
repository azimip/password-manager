import unittest

from utils.common_checker import is_common


class TestCommonChecker(unittest.TestCase):
    def test_common(self):
        password = "password"
        self.assertEqual(is_common(new_password=password), True)
