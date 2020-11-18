"""
	This test files created to test the new implementation of the function fetch.
	Test Cases:
		- Add rows to a random table
		- Make sure the fetch function retreives proper values 
		- Make sure the fetch function is able to retreive only the given number of rows.
"""
from skydb import SkydbTable
from skydb.skydb_utils import _value_in
from random import choice
from string import ascii_letters

table_name = ''.join([choice(ascii_letters) for i in range(20)]) # Generate a random table name
seed = "SEED"

table = SkydbTable(table_name, columns=['col1'], column_split=['c1','c2','c3'], seed=seed)

row_index = table.add_row({'col1':'Data-1;Data-2;Data-3'}) 
row_index = table.add_row({'col1':'Data-5;Data-6;Data-7'})
row_index = table.add_row({'col1':'Data-1;Data-2;Data-3'})
row_index = table.add_row({'col1':'Data-5;Data-6;Data-9'})

def test_fetch_2_rows():
	global table, row_index
	rows = table.fetch(
				condition={'col1':['c1','Data-5']},
				start_index=row_index,
				n_rows=2,
				condition_func=_value_in
			)
	assert len(rows) == 2, "Test case failed. The fetched rows is not the same as n_rows"
	print("-"*40)
	print(rows)
	
	for k in rows:
		assert rows[k]['col1'].split(';')[0] == 'Data-5', "Test case failed. Invalid Data retreived"

def test_fetch_1_rows():
	global table, row_index
	rows = table.fetch(
				condition={'col1':['c1','Data-5'], 'col1':['c3','Data-7']},
				start_index=row_index,
				n_rows=2,
				condition_func=_value_in
			)
	assert len(rows) == 1, "Test case failed. The fetched rows is not the same as n_rows"
	print("-"*40)
	print(rows)
	
	for k in rows:
		assert rows[k]['col1'].split(';')[0] == 'Data-5', "Test case failed. Invalid Data retreived"
		assert rows[k]['col1'].split(';')[2] == 'Data-7', "Test case failed. Invalid Data retreived"

def test_fetch_0_rows():
	global table, row_index
	rows = table.fetch(
				condition={'col1':['c1','Data-5'], 'col1':['c3','Data-10']},
				start_index=row_index,
				n_rows=2,
				condition_func=_value_in
			)
	assert len(rows) == 0, "Test case failed. The fetched rows is not the same as n_rows"
	print("-"*40)
	print(rows)

test_fetch_2_rows()
test_fetch_1_rows()
test_fetch_0_rows()
