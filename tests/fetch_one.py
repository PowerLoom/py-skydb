from skydb_utils import SkydbTable
import time

table = SkydbTable(table_name="MyTable", columns=['c1','c2'], seed="RANDOM SEED")


t = time.time()
print(table.fetch(condition={'c1':'Data 4'}, num_workers=1, mode=0))
print(time.time() - t)

