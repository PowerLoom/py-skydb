"""
    - The implementation of generating public and private key pairs will be mirrored from the
    official package skynet-js nodejs package, the crypto.ts file
"""
import nacl
import hashlib
from backports.pbkdf2 import pbkdf2_hmac # For generating the a proper 32 byte password from the seed

def blake2b(data_key):
    """
    Hash the given data_key using the blake2b algorithm to generate a 32bytes(256bits) hash
    Args:
        data_key(str): This is the data_key that will be used to retrieve entries from the registry
    """
    pass

def encode_num(num):
    """
    This function is based on the encodeNumber function on the crypto.ts file
    Args:
        num(int): This is the number that needs to be encoded
    Returns:
        encoded_num(list): A list of 8 ints which are derived from the encoded num
    """
    _bytes = (num).to_bytes(8, byteorder='little')
    encoded_num = list(_bytes)
    return encode_num


def genKeyPairFromSeed(seed):
    """
    Generate a Public key, Private Key pair from the seed using Ed25519 Algorithm
    Args:
        seed(str): Any random seed can be used. Make sure to remember the seed so that you
        can re-generate the public and private keys if your ever lose them.
    Returns:
        public_key(bytes), private_key(bytes): Both are public_key and private_keys.
    """
    if not isinstance(seed, str):
        raise Exception("The seed value has to be a string")

    seed = seed.encode("utf-8")
    key = pbkdf2_hmac("sha256", seed, b"", 1000, 32)
    return nacl.bindings.crypto_sign_seed_keypair(key)


