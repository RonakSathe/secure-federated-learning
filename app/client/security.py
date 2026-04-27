from cryptography.fernet import Fernet
import pickle

key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_params(params):
    return cipher.encrypt(pickle.dumps(params))

def decrypt_params(encrypted_params):
    return pickle.loads(cipher.decrypt(encrypted_params))