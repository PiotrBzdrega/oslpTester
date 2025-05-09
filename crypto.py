import ssl
from enum import Enum
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

PRIVATE_KEY = "/keys/platform_ecdsa_private.pem" #"/mnt/nvm/OSLitaP/keys/private_sim_key.der"
PUBLIC_KEY = "/keys/device_ecdsa_public.pem"#"/mnt/nvm/OSLitaP/keys/public_sim_key.der" 

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
            key =  serialization.load_pem_public_key(key_file.read())
        else:
            key =  serialization.load_pem_private_key(key_file.read(),password=None)
    return key


def sign(key,data) -> bytes:
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

def signatureTest():
    public_key = load_key(PUBLIC_KEY,public=True)
    private_key =load_key(PRIVATE_KEY,public=False)

    print(public_key)
    print(private_key)
    data = bytes([1,2,3,4])
    signature = sign(private_key,data)
    print("signature " + str(signature.hex()))
    decimal_string = ",".join(str(byte) for byte in signature)
    print(decimal_string)
    verify(public_key,data,signature)