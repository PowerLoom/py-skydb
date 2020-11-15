from skydb_utils import SkydbTable

table = SkydbTable(table_name="MyTable", columns=['c1','c2'], seed="RANDOM SEED")

_ = table.add_row({'c1':'Data 1', 'c2': 'HoHoHo a'})
_ = table.add_row({'c1':'Data 2', 'c2': 'HoHoHo b'})
_ = table.add_row({'c1':'Data 3', 'c2': 'HoHoHo c'})
_ = table.add_row({'c1':'Data 4', 'c2': 'HoHoHo d'})

print(table.fetch_row(0))
print(table.fetch_row(1))
print(table.fetch_row(2))
print(table.fetch_row(3))
