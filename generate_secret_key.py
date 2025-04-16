#!/usr/bin/env python3
import secrets

def generate_secret_key(length=32):
    """Generate a secure random key suitable for Flask SECRET_KEY"""
    return secrets.token_hex(length)

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print(f"\nGenerated SECRET_KEY: {secret_key}\n")
    print("To use this key, add it to your .env file:")
    print(f"SECRET_KEY={secret_key}\n") 