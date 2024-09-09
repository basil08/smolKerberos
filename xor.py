import base64
import json


# Fails for certain characters
# I am guessing it's because of character boundary issues

# Function to derive a key from an arbitrary length key using a simple hash function (sum of character codes)
def derive_key(key):
    # Simple hash function to get a key for the XOR cipher
    hash_value = sum(ord(char) for char in key) % 256
    return hash_value

# Function to encrypt data using XOR cipher
def encrypt_data(data, key):
    derived_key = derive_key(key)
    data_str = json.dumps(data)  # Convert JSON data to string
    encrypted_data = bytearray()
    for char in data_str:
        encrypted_data.append(ord(char) ^ derived_key)  # XOR each character with the key
    return base64.urlsafe_b64encode(encrypted_data).decode()  # Encode to base64 for safe transport

# Function to decrypt data using XOR cipher
def decrypt_data(encrypted_data, key):
    derived_key = derive_key(key)
    encrypted_data_bytes = base64.urlsafe_b64decode(encrypted_data.encode())  # Decode from base64
    decrypted_data = bytearray()
    for byte in encrypted_data_bytes:
        decrypted_data.append(byte ^ derived_key)  # XOR each byte with the key
    data_str = decrypted_data.decode()
    data_decoded = json.loads(data_str)  # Convert string back to JSON
    return data_decoded

# Main execution
if __name__ == '__main__':
    # Sample key (user-provided, arbitrary length)
    user_key = "my_super_secret_key"

    # Sample data
    data = { "username": "username" }

    # Encrypt the data
    encrypted_data = encrypt_data(data, user_key)
    print(f"Encrypted data: {encrypted_data}")

    # Decrypt the data
    decrypted_data = decrypt_data(encrypted_data, user_key)
    print(f"Decrypted data: {decrypted_data}")

