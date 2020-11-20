from skydb import RegistryEntry
from skydb.crypto import genKeyPairFromSeed
import json
import string
import random

pk, sk = genKeyPairFromSeed("My Seed")
re = RegistryEntry(pk, sk)
key = ''.join([random.choice(string.ascii_letters) for i in range(20)])
sent_data = ''.join([random.choice(string.ascii_letters) for i in range(100)])

re.set_entry(key, sent_data, 1)
retrieved_data,revision =  re.get_entry(key)
print(revision)
retrieved_data,revision =  re.get_entry(key)
print(revision)
retrieved_data,revision =  re.get_entry(key)
print(revision)
retrieved_data,revision =  re.get_entry(key)
print(revision)
retrieved_data,revision =  re.get_entry(key)
print(revision)
retrieved_data,revision =  re.get_entry(key)
print(revision)

assert sent_data == retrieved_data, "Test Case Failed, The retrieved data is not the same as the sent data"
