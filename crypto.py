import ssl
from enum import Enum
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

TEST_PRIVATE_KEY = "/mnt/nvm/OSLitaP/keys/private_sim_key.der"
TEST_PUBLIC_KEY = "/mnt/nvm/OSLitaP/keys/public_sim_key.der" 

def create_hash(data):
    # Create a SHA-256 hash object
    digest = hashes.Hash(hashes.SHA256())

    # Update the hash object with the data (must be bytes)
    digest.update(data.encode())  # Assuming 'data' is a string
    
    # Finalize the hash and get the digest
    hash_value = digest.finalize()

    return hash_value

def load_key(path,public: bool):
    with open(path,"rb") as key_file:
        if public:
            key =  serialization.load_der_public_key(key_file.read())
        else:
            key =  serialization.load_der_private_key(key_file.read(),password=None)
    return key


def sign(key,data):
    return key.sign(data,ec.ECDSA(hashes.SHA256()))

def verify(key,data,signature): 
   # Verify the signature
    try:
        key.verify(
            signature,
            data,
            ec.ECDSA(hashes.SHA256())
        )
        print("Signature is valid.")
        return True
    except Exception as e:
        print("Signature is invalid:", e)
        return False
