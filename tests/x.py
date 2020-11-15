from skydb_utils import RegistryEntry
from crypto import genKeyPairFromSeed

pk, sk = genKeyPairFromSeed("My Seed")
re = RegistryEntry(pk, sk)
re.set_entry("KEY1", "My Data", 3)
