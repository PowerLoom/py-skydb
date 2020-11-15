from crypto import hash_data_key, hash_all
from crypto import encode_string,encode_num
from crypto import genKeyPairFromSeed

import requests
from requests.exceptions import Timeout
import json
import nacl.bindings

import threading

class SkydbTable(object):
	"""
	- The main goals with this class will be to implement basic database functions such as add_rows,
	edit_rows, fetchone, fetchall
	"""

	def __init__(self, table_name:str, columns:list, seed:str):
		"""
		Args:
			table_name(str): This is the name of the table and will also act as key in the 
			skydb registry.

			columns(list): This parameter will name all the columns of the table. In general I 
			plan of setting each of the row as multiple key -> value pairs with key being the
			table_name:column_name:row_index and the value will be data stored at that (row i.e. index, column)
			place.

			seed(str): This is an important parameter. The seed will be used to generate the same
			public and private key pairs. If the seed is lost then access to the data entrys in the 
			registry will also be lost.
		"""
		self.table_name = table_name
		self.seed = seed
		self.columns = columns

		# Initialize the Registry
		self._pk, self._sk = genKeyPairFromSeed(self.seed)
		self.registry = RegistryEntry(self._pk, self._sk)
		
		# The index will be checked for and if there was no such table before then the index will be zero
		self.index, self._index_revision = self.get_index()
	
	def get_index(self) -> int:
		"""
		- Check if the table existed before, if so then retrieve its index and return it else
		return 0. If a Timeout exception is raised then that means that the required data is not available at 
		the moment.
		"""
		try:
			index, revision = self.registry.get_entry(f"INDEX:{self.table_name}", timeout=5)
			return int(index), revision
		except Timeout as T:
			print("Initializing the index...")
			self.registry.set_entry(data_key=f"INDEX:{self.table_name}", data=f"{0}", revision=1)
			return (0,1)

	def add_row(self, row:dict) -> int:
		"""
		Args:
			row(dict): this dictionary must have all the keys that have been passed as columns 
			while initializing this object.
		Returns:
			latest_index(int): This value represents the index of the added row

		"""
		# Check for invalid column names
		for k in row.keys():
			if k not in self.columns:
				raise ValueError("An invalid column has been passed.")

		# Check if all the columns are filled or not
		for k in self.columns:
			if k not in list(row.keys()):
				raise ValueError(f"Column {k} is empty")

		
		# Add data to the registry one by one
		for key in row.keys():
			self.registry.set_entry(
					data_key=f"{self.table_name}:{key}:{self.index}",
					data=f"{row[key]}",
					revision=1
				)

		self.index += 1
		self.registry.set_entry(f"INDEX:{self.table_name}",f"{self.index}", self._index_revision+1)
		self._index_revision += 1

		return self.index - 1

	def fetch_row(self, row_index:int) -> dict:
		"""
		Args:
			row_index(int): The index of the row that you want to fetch
		"""
		if row_index >= self.index or row_index < 0:
			raise ValueError(f"row_index={row_index} is invalid. It should in the range of 0-{self.index}")

		row = {}
		for c in self.columns:
			data, revision = self.registry.get_entry(data_key=f"{self.table_name}:{c}:{row_index}")
			row[c] = data

		return row

	def _fetch(self, condition:dict, work_index:int, n_skip:int):
		""" 
		This function is meant to be run as a thread.
		It will check for conditions an initiate flags once the row is found.
		"""
			
		keys_satisfy = False
		while not self.found:
			if work_index >= self.index:
				break

			for k in condition.keys():
				data, revision = self.registry.get_entry(
								data_key=f"{self.table_name}:{k}:{work_index}"
							)
				if condition[k] != data:
					keys_satisfy = False
					break
				else:
					keys_satisfy = True

			if not keys_satisfy:
				work_index += n_skip
			else:
				self.fetch_lock.acquire()
				if not self.found:
					self.found = True
					self.fetch_index = work_index
				self.fetch_lock.release()	

	def fetch_one(self, condition:dict, num_workers=2) -> dict:
		"""
		This function will fetch a row which satifies the condition. The condition can be something like
		{'c1':'data 1', 'c2':'JeJa'}. The first row with those values will be returned

		Args:
			condition(dict): This variable is basically the values that will be in the row 
			that you want to fetch
		"""
		# Make sure the condition is not empty
		assert len(condition) > 0, "The condition should not be empty"

		# Check if the keys are valid column names
		for k in condition.keys():
			assert k in self.columns, f"Invalid column name: {k}"

	
		self.found = False
		self.fetch_index = -1
		self.fetch_lock = threading.Lock()

		threads = [threading.Thread(target=self._fetch, args=(condition,i,num_workers))\
				for i in range(num_workers)]

		for t in threads:
			t.start()

		for t in threads:
			t.join()

		if self.found == False:
			return {}
		else:
			return self.fetch_row(row_index=self.fetch_index)


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

		def get_entry(self, data_key:str, timeout:int=2) -> str:
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
		response = requests.get(self._endpoint_url, params=querry, timeout=timeout)
		response_data = json.loads(response.text)
		revision = response_data['revision']
		data = bytearray.fromhex(response_data['data']).decode()
		return (data, revision)
