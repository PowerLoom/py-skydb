"""
	- The implementation of generating public and private key pairs will be mirrored from the
	official package skynet-js nodejs package, the crypto.ts file
"""
import nacl
import nacl.bindings
import hashlib
from backports.pbkdf2 import pbkdf2_hmac # For generating the a proper 32 byte password from the seed


def encode_num(num:int) -> list:
	"""
	This function is based on the encodeNumber function on the crypto.ts file
	Args:
		num(int): This is the number that needs to be encoded
	Returns:
		encoded_num(list): A list of 8 ints which are derived from the encoded num
	"""
	_bytes = (num).to_bytes(8, byteorder='little')
	encoded_num = list(_bytes)
	return encoded_num

def encode_string(text:str) -> list:
	"""
	This function is based on the encodeString function on the crypto.ts file
	Args:
		text(str): The string that needs to be encoded
	Returns:
		encoded_text(list): A list of ints which represent the string
	"""
	encoded_num = encode_num(len(text))
	encoded_text = encoded_num + list(text.encode())
	return encoded_text

def hash_data_key(data_key:str) -> str:
	"""
		This function is based on the hashDataKey function in crypto.ts file.
		given a data key, encode it into a list of ints and hash the entire list using
		blake2b algo, and return the hex string of the hash
		Args:
			data_key(str): The data_key that needs to be hashed
		Returns:
			hashed_data_key(str): The hash of the data_key in string form
	"""
	encoded_data_key = encode_string(data_key)
	h = hashlib.blake2b(digest_size=32)
	# important to convert the list of ints to bytes
	h.update(bytes(encoded_data_key))
	return h.hexdigest()

def hash_all(data:list) -> bytes:
	"""
		- Do a hash on all of the given data
		Returns:
			hash_data(bytes): Note that this function returns bytes and not a hex string
	"""
	h = hashlib.blake2b(digest_size=32)
	for d in data:
		if isinstance(d, str):
			h.update(d.encode())

		elif isinstance(d, list):
			h.update(bytes(d))

		else:
			raise ValueError("An invalid type of data has been passed. This function only processese string and lists")
	return h.digest()


def genKeyPairFromSeed(seed:str) -> tuple:
	"""
	Generate a Public key, Private Key pair from the seed using Ed25519 Algorithm
	Args:
		seed(str): Any random seed can be used. Make sure to remember the seed so that you
		can re-generate the public and private keys if your ever lose them.
	Returns:
		public_key(bytes), private_key(bytes): Both are public_key and private_keys.
	"""
	if not isinstance(seed, str):
		raise Exception("The seed value has to be a string")

	seed = seed.encode("utf-8")
	key = pbkdf2_hmac("sha256", seed, b"", 1000, 32)
	return nacl.bindings.crypto_sign_seed_keypair(key)


