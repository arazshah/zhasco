"""Small helpers to keep a secret (mailbox password) encrypted in the database."""
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet():
    key = base64.urlsafe_b64encode(hashlib.sha256(("zhasco-mail:" + settings.SECRET_KEY).encode()).digest())
    return Fernet(key)


def encrypt(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode() if value else ""


def decrypt(token: str) -> str:
    """Returns '' if the token is empty or cannot be decrypted (e.g. SECRET_KEY changed)."""
    if not token:
        return ""
    try:
        return _fernet().decrypt(token.encode()).decode()
    except (InvalidToken, ValueError):
        return ""
