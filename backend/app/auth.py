# app/auth.py

import hashlib


def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a SHA-256 hash.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check whether the plain password matches the stored hash.
    """
    return hash_password(plain_password) == hashed_password
