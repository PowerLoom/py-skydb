from skydb_utils import SkydbTable
import time

table = SkydbTable(table_name="MyTable", columns=['c1','c2'], seed="RANDOM SEED")


t = time.time()
print(table.fetch_one(condition={'c1':'Data 4', 'c2':'HoHoHo d'}, num_workers=6))
print(time.time() - t)

