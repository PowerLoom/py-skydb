from crypto import hash_data_key, hash_all
from crypto import encode_string,encode_num

import requests
import json
import nacl.bindings

class RegistryEntry(object):

	def __init__(self, public_key:bytes, private_key:bytes, endpoint_url:str="https://siasky.net/skynet/registry"):
		"""
		Args:
			private_key(bytes), public_key(bytes): These two keys are responsible to sign and verify the 
			messages that will sent and retreived from the skynet

		"""
		
		self._pk = public_key
		self._sk = private_key
		self._endpoint_url = endpoint_url
		# This below variable refers to max size of the signed message
		self._max_len = 64



	def set_entry(self, data_key:str, data:str, revision:int) -> bool:
		"""
			- This function is based on the setEntry function of registry.ts.
			- Basically add an entry into the skynet with data_key as the key

		"""
		# First sign the data
		hash_entry = hash_all((
				list(bytearray.fromhex(hash_data_key(data_key))),
				encode_string(data),
				encode_num(revision),
			))
		raw_signed = nacl.bindings.crypto_sign(hash_entry, self._sk)


		# The public key needs to be encoded into a list of integers. Basically convert hex -> bytes
		public_key = {'algorithm': "ed25519", 'key': list(self._pk)}

		
		_data_key = hash_data_key(data_key)
		_data = list(data.encode())
		_signature = list(raw_signed)[:self._max_len]

		post_data = {
				'publickey': public_key,
				'datakey': _data_key,
				'revision': revision,
				'data': _data,
				'signature': _signature,
			}
		print(json.dumps(post_data))

		response = requests.post(self._endpoint_url, data=json.dumps(post_data))
		print(response.status_code)
		print(response.text)


	def get_entry(self, data_key:str) -> str:
		pass

