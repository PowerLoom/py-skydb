from skydb_utils import RegistryEntry
from crypto import genKeyPairFromSeed
import json

pk, sk = genKeyPairFromSeed("My Seed")
re = RegistryEntry(pk, sk)
#re.set_entry("KEY3", "data", 1)
data =  json.loads(re.get_entry("KEY3"))
print(bytearray.fromhex(data['data']).decode())
