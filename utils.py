import base64, json

def derive_key(key):
    # Simple hash function to get a key for the XOR cipher
    hash_value = sum(ord(char) for char in key) % 256
    return hash_value

def encrypt_data(payload, key):
    derived_key = derive_key(key)
    encrypted_data = bytearray()
    data_str = json.dumps(payload)
    data_bytes = data_str.encode('utf-8')
    for byte in data_bytes:
        encrypted_data.append(byte ^ derived_key)  # XOR each character with the key
    encrypted_data = base64.urlsafe_b64encode(encrypted_data).decode('utf-8')

    # padding_needed = 4 - len(encrypted_data) % 4

    # if padding_needed:
    #     encrypted_data += "=" * padding_needed  # Add the necessary padding

    print("debug", encrypted_data)
    return encrypted_data

# Function to decrypt data using XOR cipher
def decrypt_data(encrypted_data, key):
    padding_needed = 4 - len(encrypted_data) % 4

    print(len(encrypted_data))
    print(encrypted_data.encode())
    print(padding_needed)
    encrypted_data += '=' * (-len(encrypted_data) % 4)

    print(encrypted_data.encode())
    print(len(encrypted_data))

    derived_key = derive_key(key)
    encrypted_data_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))  # Decode from base64
    decrypted_data = bytearray()
    for byte in encrypted_data_bytes:
        decrypted_data.append(byte ^ derived_key)  # XOR each byte with the key
    data_str = decrypted_data.decode('utf-8')
    data_decoded = json.loads(data_str)  # Convert string back to JSON
    return data_decoded
