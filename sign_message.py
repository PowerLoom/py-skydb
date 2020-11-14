from crypto import genKeyPairFromSeed
import nacl.bindings

pk, sk = genKeyPairFromSeed("My Seed")
print(pk.hex())
print(sk.hex())
print()

message = bytes([1,2,3,4,5])
raw_signed = nacl.bindings.crypto_sign(message, sk)
data = list(raw_signed)[:64]
print(data)
