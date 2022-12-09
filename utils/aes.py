
import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

def encrypt(key, plain_text):
	plain_text = plain_text.encode()

	key = key.encode()
	key = SHA256.new(key).digest()

	IV = Random.new().read(AES.block_size)

	encryptor = AES.new(key, AES.MODE_CBC, IV)
	pad = AES.block_size - len(plain_text) % AES.block_size
	plain_text += bytes([pad]) * pad
	data = IV + encryptor.encrypt(plain_text)

	return base64.b64encode(data).decode()

def decrypt(key, ciphertext):
	ciphertext = ciphertext.encode()
	ciphertext = base64.b64decode(ciphertext)

	key = key.encode()
	key = SHA256.new(key).digest()  

	IV = ciphertext[:AES.block_size]

	decryptor = AES.new(key, AES.MODE_CBC, IV)
	data = decryptor.decrypt(ciphertext[AES.block_size:])
	pad = data[-1]

	if data[-pad:] != bytes([pad]) * pad:
		raise ValueError("Invalid pad...")
	return data[:-pad].decode()
