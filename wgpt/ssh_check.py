from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend


def generate_keys():
    print('Generating and storing ssh keys')
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption())
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH,
        crypto_serialization.PublicFormat.OpenSSH
    )

    private_lines = private_key.decode().split('\n')
    private_lines[0] = '-----BEGIN RSA PRIVATE KEY-----'
    private_lines[-2] = '-----END RSA PRIVATE KEY-----'
    private_key = '\n'.join(private_lines).encode()

    return private_key, public_key
