# raghav-repo
### This is sample repo that will be used to store and retrieve data from the Registry
### Usage:

```python
from skydb_utils import RegistryEntry
from crypto import genKeyPairFromSeed
import json
pk, sk = genKeyPairFromSeed("Some Random Seed TEXT")
re = RegistryEntry(pk, sk)
re.set_entry(data_key="KEY1", data="Some data", revision=1)
data = json.loads(re.get_entry(data_key="KEY1"))['data']
data = bytearray.fromhex(data).decode()
print(data)
```
