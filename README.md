# py-skydb

A Simple Python Wrapper that you can use to interact with SkyDB portals. You can use the SkydbTable to store rows into Skydb
or you can directly use the RegistryEntry class to store key:value pairs.

### SkydbTable Usage:
```python
from skydb import SkydbTable

table = SkydbTable(table_name="SomeRandomTableName", columns=['c1','c2'], seed="RANDOM SEED")

index_ = table.add_row({'c1':'Data 1', 'c2': 'HoHoHo'})
index_ = table.add_row({'c1':'Data 2', 'c2': 'HoHoHo'})
index_ = table.add_row({'c1':'Data 3', 'c2': 'HoHoHo'})
index_ = table.add_row({'c1':'Data 4', 'c2': 'HoHoHo'})
index_ = table.add_row({'c1':'Data 5', 'c2': 'HoHoHo'})
index_ = table.add_row({'c1':'Data 4', 'c2': 'NewData'})

print(table.fetch_row(row_index=0))
print(table.fetch_row(row_index=1))
print(table.fetch_row(row_index=2))
print(table.fetch_row(row_index=3))

# The start_index refers to the index from where you want to start fetching rows. The function will fetch rows which match the condition from start_index to 0 
print(table.fetch(condition={'c1':'Data 4'}, start_index=table.index-1, n_rows=1, num_workers=2)) # fetch one row

print(table.fetch(condition={'c1':'Data 4'}, start_index=table.index-1, n_rows=3, num_workers=2)) # fetch three rows

print(table.fetch(condition={'c1':'Data 4','c2':'NewData'}, start_index=table.index-1, n_rows=3, num_workers=2)) 

# Update the row with new data
table.update_row(row_index=5, data={'c1':'SomeNewUpdateData'})
print(table.fetch_row(row_index=5))


""" Check if a table exists """
out = SkydbTable.check_table(table_name="table_name", seed="xyz")
if out is None:
	print("The table does not exist")
else:
	print(f"The table exists at index {out[0]}, with revision {out[1]}")
	
	
""" Using a condition function """
"""
If there is a certain condition that you want to match against a certain row for example, if you want to match rows that have 
first letter as D and last letter 4 in their column c1, you can specificially write a seperate function to do that and then pass 
that function as an argument to the table.fetch function
"""

def check_start_D(condition, key, value, column_split) -> bool:
    '''
    args:
    	condition(dict): This is the condition variable that you passed.
	key(str): The column that is being processed right now
	value(str): The value for the column(key) in the Skydb
	column_split(list): If by any chance  you want to combine all the columns in to single column, you can mention the column_split while initializing 
	the table. It defaults to None.	
    '''
    if (key=='c1') and (value[0] == 'D') and (value[-1] == '4'):
        return True
    else:
        return False
	
row = table.fetch(
	    condition={'c1':''}, # Leave it empty if you dont want to match any kind of text
	    start_index=table.index-1, # The table.index-1 gives you the index of the last added row
	    n_rows=2,
	    condition_func=check_start_D # Your condition function
	)
    
```

### Registry Entry Usage:
```python
from skydb import RegistryEntry
from skydb.crypto import genKeyPairFromSeed
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

	- The get_entry  will throw a Timeout Exception if it was not able to find the data for that key. I am not handling that exception in the get_entry function. You will have to explicitly try to catch that one.
