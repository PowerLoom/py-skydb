from skydb import SkydbTable
from random import choice
from string import ascii_letters

table_name = ''.join([choice(ascii_letters) for i in range(20)])
import time

print("Creating table")
table = SkydbTable(table_name, columns=['c1','c2','c3'], seed="some_random", verbose=1)
print("Added table successfully")

def test_mass_fetch():
	global table

	rows = []
	for i in range(20):
		row = {}
		for c in ['c1', 'c2','c3']:
			row['c1'] = ''.join([choice(ascii_letters) for i in range(5)])
			row['c2'] = ''.join([choice(ascii_letters) for i in range(5)])
			row['c3'] = ''.join([choice(ascii_letters) for i in range(5)])
		rows.append(row)

	print("Adding rows")
	table.add_rows(rows)
	print("Successfully added rows")

	out = table.fetch_rows(list(range(10)))


