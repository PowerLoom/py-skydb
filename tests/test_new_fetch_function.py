"""
	This test files created to test the new implementation of the function fetch.
	Test Cases:
		- Add rows to a random table
		- Make sure the fetch function retreives proper values 
		- Make sure the fetch function is able to retreive only the given number of rows.
"""
from skydb import SkydbTable
from random import choice
from string import ascii_letters

table_name = ''.join([choice(ascii_letters) for i in range(20)]) # Generate a random table name
seed = "SEED"

table = SkydbTable(table_name, columns=['c1','c2','c3'], seed=seed)

row_index = table.add_row({'c1':'Data-1', 'c2':'Data-2', 'c3': 'Data-3'}) 
row_index = table.add_row({'c1':'Data-5', 'c2':'Data-6', 'c3': 'Data-6'})
row_index = table.add_row({'c1':'Data-1', 'c2':'Data-2', 'c3': 'Data-3'})
row_index = table.add_row({'c1':'Data-5', 'c2':'Data-6', 'c3': 'Data-6'})

def test_fetch_2_rows():
	global table, row_index
	rows = table.fetch(
				condition={'c1':'Data-5','c2':'Data-6'},
				start_index=row_index,
				n_rows=2
			)
	assert len(rows) == 2, "Test case failed. The fetched rows is not the same as n_rows"
	
	for k in rows:
		assert rows[k]['c1'] == 'Data-5', "Test case failed. Invalid Data retreived"
		assert rows[k]['c2'] == 'Data-6', "Test case failed. Invalid Data retreived"

def test_fetch_none():
	global table, row_index
	rows = table.fetch(
				condition={'c1':'Data-10','c2':'Data-6'},
				start_index=row_index,
				n_rows=2
			)
	assert len(rows) == 0, "Test case failed. The fetched rows is not the same as n_rows"

test_fetch_2_rows()
test_fetch_none()
