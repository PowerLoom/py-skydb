from skydb import SkydbTable

table = SkydbTable(table_name="asdacxccaf", columns=['c1','c2'], seed="RANDOM SEED")

_ = table.add_row({'c1':'Data 1', 'c2': 'HoHoHo a'})
_ = table.add_row({'c1':'Data 2', 'c2': 'HoHoHo b'})
_ = table.add_row({'c1':'Data 3', 'c2': 'HoHoHo c'})
_ = table.add_row({'c1':'Data 4', 'c2': 'HoHoHo d'})
print('fetching a table')
print(table.fetch_row(3))

print(table.fetch(condition={'c1':'Data 2'}, start_index=_))
