# raghav-repo
### SkydbTable Usage:
```python
from skydb_utils import SkydbTable

table = SkydbTable(table_name="SomeRandomTableName", columns=['c1','c2'], seed="RANDOM SEED")

_ = table.add_row({'c1':'Data 1', 'c2': 'HoHoHo'})
_ = table.add_row({'c1':'Data 2', 'c2': 'HoHoHo'})
_ = table.add_row({'c1':'Data 3', 'c2': 'HoHoHo'})
_ = table.add_row({'c1':'Data 4', 'c2': 'HoHoHo'})

print(table.fetch_row(row_index=0))
print(table.fetch_row(row_index=1))
print(table.fetch_row(row_index=2))
print(table.fetch_row(row_index=3))

print(table.fetch_one(condition={'c1':'Data 4'}, num_workers=2))
```

### Registry Entry Usage:
```python
from skydb_utils import RegistryEntry
from crypto import genKeyPairFromSeed
from requests.exception import Timeout

pk, sk = genKeyPairFromSeed("Some Random Seed TEXT")
re = RegistryEntry(pk, sk)
re.set_entry(data_key="KEY1", data="Some data", revision=1)
try:
	data, revision = re.get_entry(data_key="KEY1")
	print(data)
except Timeout as T:
	print("The key:data pair does not exist")
```

NOTE:
	
	- The max data size that you can put in the registry is 113 bytes or 113 characters.

	- Using the same seed, do not try to set_entry same the key:data pair with the same revision. Once the key:data pair is set in the database, you need to keep track of the revisions every time you want to edit that entry.

	- The same seed will always output same public, private key pairs.

	- The get_entry  will throw a Timeout Exceptio if it was not able to find the data for that key. I am not handling that exception in the get_entry function. You will have to explicitly try to catch that one.
