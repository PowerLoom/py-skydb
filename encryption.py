"""
    - The implementation of generating public and private key pairs will be mirrored from the
    official package skynet-js nodejs package, the crypto.ts file
"""
import nacl
from backports.pbkdf2 import pbkdf2_hmac # For generating the a proper 32 byte password from the seed

def genKeyPairFromSeed(seed):
    """
    Generate a Public key, Private Key pair from the seed using Ed25519 Algorithm
    Returns:
        public_key(bytes), private_key(bytes): Both are public_key and private_keys.
    """
    if not isinstance(seed, str):
        raise Exception("The seed value has to be a string")

    seed = seed.encode("utf-8")
    key = pbkdf2_hmac("sha256", seed, b"", 1000, 32)
    return nacl.bindings.crypto_sign_seed_keypair(key)
