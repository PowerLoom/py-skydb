from skydb import SkydbTable
from random import choice
from string import ascii_letters

def test_check_table():

	table_name = ''.join([choice(ascii_letters) for i in range(100)])
	seed = ''.join([choice(ascii_letters) for i in range(34)])

	out = SkydbTable.check_table(table_name, seed)
	assert out == None, f"Test case failed, The table: {table_name} should not exist."

	table = SkydbTable(table_name, columns=['c1'], seed=seed)
	out = SkydbTable.check_table(table_name, seed)
	assert len(out) == 2, f"The function check_table is not returning proper outputs: {out}"
	assert out[0] == 0, "The function check_table is return invalid index: {out[0]} for index {table.index-1}"
	assert out[1] == table._index_revision, f"The function check_table is returning invalid index_revision: {out[1]} for {table._index_revision}"

	print("All test cases passed")
