from skydb_utils import RegistryEntry
from crypto import genKeyPairFromSeed
import json
import string
import random

pk, sk = genKeyPairFromSeed("My Seed")
re = RegistryEntry(pk, sk)
key = ''.join([random.choice(string.ascii_letters) for i in range(20)])
sent_data = ''.join([random.choice(string.ascii_letters) for i in range(50)])

re.set_entry(key, sent_data, 1)
retrieved_data =  re.get_entry(key)


assert sent_data == retrieved_data, "Test Case Failed, The retrieved data is not the same as the sent data"
