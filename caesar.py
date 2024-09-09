import json



def encrypt_data(data, key):
    alphabets = "abcdefghijklmnopqrstuvwxyz"
    numbers = "0123456789"
    special_chars = "!@#$%^&*()_+[]{}|;':,.<>?/"
    # implement a caesar cipher
    # shift the characters by the key
    # if the character is a number, shift the number by the key
    # if the character is a special character, shift the special character by the key
    # if the character is a space, keep it as a space
    # if the character is a letter, shift the letter by the key
    # return the encrypted data
    encrypted_data = ""
    for char in data:
        if char.isalpha():
            if char.islower():
                encrypted_data += alphabets[(alphabets.index(char) + key) % 26]
            else:
                encrypted_data += alphabets[(alphabets.index(char.lower()) + key) % 26].upper()
        elif char.isdigit():
            encrypted_data += numbers[(numbers.index(char) + key) % 10]
        elif char in special_chars:
            encrypted_data += special_chars[(special_chars.index(char) + key) % len(special_chars)]
        elif char == " ":
            encrypted_data += " "
    return encrypted_data

def decrypt_data(encrypted_data, key):
    alphabets = "abcdefghijklmnopqrstuvwxyz"
    numbers = "0123456789"
    special_chars = "!@#$%^&*()_+[]{}|;':,.<>?/"
    # implement a caesar cipher
    # shift the characters by the key
    # if the character is a number, shift the number by the key
    # if the character is a special character, shift the special character by the key
    # if the character is a space, keep it as a space
    # if the character is a letter, shift the letter by the key
    # return the encrypted data
    decrypted_data = ""
    for char in encrypted_data:
        if char.isalpha():
            if char.islower():
                decrypted_data += alphabets[(alphabets.index(char) - key) % 26]
            else:
                decrypted_data += alphabets[(alphabets.index(char.lower()) - key) % 26].upper()
        elif char.isdigit():
            decrypted_data += numbers[(numbers.index(char) - key) % 10]
        elif char in special_chars:
            decrypted_data += special_chars[(special_chars.index(char) - key) % len(special_chars)]
        elif char == " ":
            decrypted_data += " "
    return decrypted_data


def main():
    # Sample key (user-provided, arbitrary length)
    user_key = 5
    cleartext = "{ username: basil }"
    print(f"Original data: {cleartext}")
    # Encrypt the data
    encrypted_data = encrypt_data(cleartext, user_key)
    print(f"Encrypted data: {encrypted_data}")
    # Decrypt the data
    decrypted_data = decrypt_data(encrypted_data, user_key)
    print(f"Decrypted data: {decrypted_data}")


if __name__ == "__main__":
    main()