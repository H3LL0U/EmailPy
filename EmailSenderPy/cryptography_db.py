import dotenv
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
dotenv.load_dotenv()
config = dotenv.dotenv_values()
config = dict(os.environ) | config  # adding environment values on top of .env


def convert_string_to_urlsafe_base64(string_to_encode: str) -> bytes:
    """Generate a 16-byte key from a string using SHA256 and Base64 encoding."""
    hash_value = hashlib.sha256(string_to_encode.encode()).digest()
    return base64.urlsafe_b64encode(hash_value[:16])


def encrypt_value(value: str, key: bytes = convert_string_to_urlsafe_base64(config["ENCRYPTION_KEY"])) -> str:
    """Encrypt a given value deterministically using AES-ECB."""
    cipher = AES.new(base64.urlsafe_b64decode(key), AES.MODE_ECB)
    encrypted_bytes = cipher.encrypt(pad(value.encode(), AES.block_size))
    return base64.urlsafe_b64encode(encrypted_bytes).decode()


def decrypt_value(value: str, key: bytes = convert_string_to_urlsafe_base64(config["ENCRYPTION_KEY"])) -> str:
    """Decrypt a given value using AES-ECB."""
    cipher = AES.new(base64.urlsafe_b64decode(key), AES.MODE_ECB)
    decrypted_bytes = unpad(cipher.decrypt(
        base64.urlsafe_b64decode(value)), AES.block_size)
    return decrypted_bytes.decode()
