from crypto import hash_data_key, hash_all
from crypto import encode_string,encode_num
from crypto import genKeyPairFromSeed

import requests
import json
import nacl.bindings

class SkydbTable(object):
	"""
	- The main goals with this class will be to implement basic database functions such as add_rows,
	edit_rows, fetchone, fetchall
	"""

	def __init__(self, table_name:str, seed:str):
		"""
		Args:
			table_name(str): This is the name of the table and will also act as key in the 
			skydb registry.

			seed(str): This is an important parameter. The seed will be used to generate the same
			public and private key pairs. If the seed is lost then access to the data entrys in the 
			registry will also be lost.
		"""
		self.table_name = table_name
		self.seed = seed
		self._pk, self._sk = genKeyPairFromSeed(self.seed)
		
		# The index will be checked for and if there was no such table before then the index will be zero
		self.index = self.get_index()
	
	def get_index(self) -> int:
		"""
		- Check if the table existed before, if so then retrieve its index and return it else
		return 0
		"""
		pass

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
		self._max_data_size = 113



	def set_entry(self, data_key:str, data:str, revision:int) -> bool:
		"""
			- This function is based on the setEntry function of registry.ts.
			- Basically add an entry into the skynet with data_key as the key

		"""
		# Make sure that the data size does not exceed the max bytes
		assert len(data) <= self._max_data_size, f"The data size({len(data)}) exceeded the limit of {self._max_data_size}."

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

		response = requests.post(self._endpoint_url, data=json.dumps(post_data))
		if response.status_code == 204:
			print("Data Successfully stored in the Registry")
		else:
			print(response.text)
			raise Exception("""
			The Registry Data was Invalid. Please do recheck that 
			- you are not using the same revision number to update the data. 
			- make sure that the keys used to sign the message come from the same seed value.
			""")

	def get_entry(self, data_key:str) -> str:
		"""
			- Get the entry given the dataKey
		"""
		publickey = f"ed25519:{self._pk.hex()}"
		datakey = hash_data_key(data_key)
		querry = {
					'publickey': publickey,
					'datakey': datakey,
				}
		# The below line will raise requests.exceptions.Timeout exception if it was unable to fetch the data 
		# in two seconds.
		response = requests.get(self._endpoint_url, params=querry, timeout=2)
		response_data = json.loads(response.text)['data']
		response_data = bytearray.fromhex(response_data).decode()
		return response_data
