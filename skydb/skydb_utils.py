from .crypto import hash_data_key, hash_all
from .crypto import encode_string,encode_num
from .crypto import genKeyPairFromSeed

import requests
from requests.exceptions import Timeout
import json
import nacl.bindings

import threading

def _equal(condition:dict, key:str, value:str, column_split:list=None) -> bool:
	return condition[key] == value

def _value_in(condition:dict, key:str, value:str, column_split:list) -> bool:
	idx = column_split.index(condition[key][0])
	value_list = value.split(';')
	return condition[key][1] == value_list[idx]

class SkydbTable(object):
	"""
	- The main goals with this class will be to implement basic database functions such as add_rows,
	edit_rows, fetchone, fetchall
	"""

	def __init__(self, table_name:str, columns:list, seed:str, column_split:list=[]):
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

			column_split(list): If you are making a single column hold all the values in the row seperated by
			';', column_split will hold the column names for each of the single values
		"""
		self.table_name = table_name
		self.seed = seed
		self.columns = columns
		self.column_split = column_split

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

	def update_row(self, row_index:int, data:dict):
		"""
		Args:
			row_index(int): The index of the row that you want to update.
			data(dict): The data that you want to update with.
		"""

		if row_index >= self.index or row_index < 0:
			raise ValueError(f"row_index={row_index} is invalid. It should in the range of 0-{self.index}")

		# Check for invalid column names
		for k in data.keys():
			if k not in self.columns:
				raise ValueError("An invalid column has been passed.")

		for k in data.keys():
			old_data, revision = self.registry.get_entry(
					data_key=f"{self.table_name}:{k}:{row_index}",
				)
			self.registry.set_entry(
					data_key=f"{self.table_name}:{k}:{row_index}",
					data=f"{data[k]}",
					revision=revision+1,
				)


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

	def _fetch(self, condition:dict, n_rows:int, work_index:int, n_skip:int, condition_func):
		""" 
		This function is meant to be run as a thread.
		It will check for conditions an initiate flags once the row is found in case of fetch_one(mode=0)
		or will update the fetched_data dictionary incase of fecth_all(mode=1)
		Args:
			condition(dict): The column values that we need to match
			n_rows(int): The max rows that we need to fetch
			work_index(int): The current working index of the thread
			n_skip(int): The no.of rows to skip for the current thread to get its next work_index

		"""
			
		keys_satisfy = False
		while True:
			if work_index < 0 or work_index >= self.index or len(self.fetched_rows) >= n_rows:
				"""
					- If the thread is on an index which is more that the no.of rows or an 
					index which is less than zero.
					- If we have reached the max no.of rows that we needed to fetch
				"""
				break

			""" For each of the given condition, check if the row at work_index matches the condition """
			for k in condition.keys():
				data, revision = self.registry.get_entry(
								data_key=f"{self.table_name}:{k}:{work_index}"
							)
				if condition_func(condition, k, data, self.column_split): # The value at the column matches the condition
					keys_satisfy = True
					break
				else:
					keys_satisfy = False


			if keys_satisfy:
				""" The condition match """
				self.fetch_lock.acquire()
				if len(self.fetched_rows) < n_rows:
					self.fetched_rows[work_index] = self.fetch_row(row_index=work_index)
				self.fetch_lock.release()	
			work_index += n_skip


	def fetch(self, condition:dict, start_index:int, n_rows:int=2, num_workers:int=2, condition_func=None) -> dict:
		"""
		- This function will fetch a row or bunch of rows, which satifies the condition. The condition can be something like
		{'c1':'data 1', 'c2':'JeJa'}. The rows with value 'data 1' at column c1 and value 'JeJa' at column c2
		will be matched and returned.

		- This function searches the rows in descending order, for example if the start_index=28, the function
		will search for rows that match the condition from row 28 all the way to row 0, until the no.of rows 
		matched are equal to n_rows.

		Args:
			Date: 18th Nov 2020
			condition(dict): This variable is basically the values that will be in the row 
			that you want to fetch

			start_index(int): The index from where the searching should start.

			n_rows(int): This variable specifies the no.of rows that I need to fetch at max in this fetch_operation.
			At this moment, the skydb portal ratelimits and throttles connections, so I will 
			not be able to continuosly send GET requests to their portal. 

			num_workers(int): This value represents the number of threads that will be assigned to search 
			for the rows

			condition_func: A function which takes condition, k, target_value and columns as arguments. You can use this 
			function along with the conditions so that a row matches that condition.

		"""
		# Make sure the condition is not empty
		assert len(condition) > 0, "The condition should not be empty"

		# Make sure that the start_index is not greater latest record and not less than zero
		assert start_index in range(0, self.index),\
						f"The start_index:{start_index} is invalid. It should in the range [0,{self.index})."

		# Check if the keys are valid column names
		for k in condition.keys():
			assert (k in self.columns or k in self.column_split), f"Invalid column name: {k}"

		self.fetch_lock = threading.Lock()
		self.fetched_rows = {}

		if condition_func == None:
			condition_func = _equal
		# We will be searching the registry from latest index to zero. That means searching will
		# take place in descending order, thats why there is `start_index-i` below
		threads = [threading.Thread(target=self._fetch, args=(condition, n_rows, start_index-i, -num_workers, condition_func))\
				for i in range(num_workers)]

		for t in threads:
			t.start()

		for t in threads:
			t.join()

		return self.fetched_rows

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
