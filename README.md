# raghav-repo
### This is sample repo that will be used to store and retrieve data from the Registry
### Usage:
```python
from skydb_utils import RegistryEntry
from crypto import genKeyPairFromSeed
from requests.exception import Timeout

pk, sk = genKeyPairFromSeed("Some Random Seed TEXT")
re = RegistryEntry(pk, sk)
re.set_entry(data_key="KEY1", data="Some data", revision=1)
try:
	data = re.get_entry(data_key="KEY1")
	print(data)
except Timeout as T:
	print("The key:data pair does not exist")
```

NOTE:
	
	- The max data size that you can put in the registry is 113 bytes or 113 characters.

	- Using the same seed, do not try to set\_entry same the key:data pair with the same revision. Once the key:data pair is set in the database, you need to keep track of the revisions every time you want to edit that entry.

	- The same seed will always output same public, private key pairs.

	- The get\_entry  will throw a Timeout Exceptio if it was not able to find the data for that key. I am not handling that exception in the get\_entry function. You will have to explicitly try to catch that one.
