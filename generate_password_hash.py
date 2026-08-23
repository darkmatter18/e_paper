#!/usr/bin/env python3
"""Generate Argon2 password hash for .env file.

Usage:
    python generate_password_hash.py

This script prompts for a password and outputs the Argon2 hash
to be stored in the AUTH_PASSWORD environment variable.
"""

import getpass
import sys

try:
    from argon2 import PasswordHasher
except ImportError:
    print("Error: argon2-cffi not installed")
    print("Run: uv sync")
    sys.exit(1)


def generate_password_hash():
    """Generate Argon2 hash for a password."""
    print("=" * 60)
    print("E-Paper Display - Password Hash Generator")
    print("=" * 60)
    print("\nThis script generates an Argon2 hash for your password.")
    print("The hash will be stored in .env as AUTH_PASSWORD\n")

    # Prompt for password
    password = getpass.getpass("Enter password: ")
    if not password:
        print("Error: Password cannot be empty")
        sys.exit(1)

    # Confirm password
    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        print("Error: Passwords do not match")
        sys.exit(1)

    # Generate hash
    ph = PasswordHasher()
    password_hash = ph.hash(password)

    print("\n" + "=" * 60)
    print("✓ Password hash generated successfully!")
    print("=" * 60)
    print("\nAdd this line to your .env file:")
    print(f'\nAUTH_PASSWORD="{password_hash}"')
    print("\nNote: This is a one-way hash. Store it safely in .env")
    print("=" * 60)


if __name__ == "__main__":
    try:
        generate_password_hash()
    except KeyboardInterrupt:
        print("\n\nAborted by user")
        sys.exit(1)
