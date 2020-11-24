from skydb import SkydbTable
from random import choice
from string import ascii_letters
table_name = ''.join([choice(ascii_letters) for i in range(20)])

def test_add_fetch_row():
	table = SkydbTable(table_name=table_name, columns=['c1','c2'], seed="RANDOM SEED", verbose=1)

	_ = table.add_row({'c1':'Data 1', 'c2': 'HoHoHo a'})
	_ = table.add_row({'c1':'Data 2', 'c2': 'HoHoHo b'})
	_ = table.add_row({'c1':'Data 3', 'c2': 'HoHoHo c'})
	_ = table.add_row({'c1':'Data 4', 'c2': 'HoHoHo d'})
	_ = table.add_row({'c1':'Data 4', 'c2': 'New d'})
	print('fetching a table')
	row = table.fetch_row(3)
	assert (row['c1'] == 'Data 4') and (row['c2'] == 'HoHoHo d'), " Test Case Failed"

	row = table.fetch(condition={'c1':'Data 2'}, start_index=_)
	print(row)
	assert next(iter(row.keys())) == 1, "Test Case Filed"

	assert row[1]['c2'] == 'HoHoHo b', "Test Case Failed"

	row = table.fetch(condition={'c1':'Data 4', 'c2':'HoHoHo d'}, start_index=_)
	print(row)
	assert (row[3]['c1'] == 'Data 4') and (row[3]['c2'] == 'HoHoHo d'), "Test Case Failed"

test_add_fetch_row()
