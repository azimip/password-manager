import unittest

from utils.strength_checker import is_strong


class TestStrengthChecker(unittest.TestCase):
    def test_no_number(self):
        password = "p@ssWord"
        self.assertEqual(is_strong(new_password=password), False)

    def test_no_special_character(self):
        password = "p4ssWord"
        self.assertEqual(is_strong(new_password=password), False)

    def test_short_password(self):
        password = "p@22Wrd"
        self.assertEqual(is_strong(new_password=password), False)

    def test_no_uppercase_password(self):
        password = "p4ssword@"
        self.assertEqual(is_strong(new_password=password), False)
