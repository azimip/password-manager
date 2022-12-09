import unittest

from utils.aes import decrypt, encrypt


class TestAES(unittest.TestCase):
    def test_aes_decrypt_ciphertext(self):
        plain_text = "thisisasecrettext"
        key = "very_good_key"

        cipher_text = encrypt(key, plain_text)

        self.assertEqual(decrypt(key, cipher_text), plain_text)
