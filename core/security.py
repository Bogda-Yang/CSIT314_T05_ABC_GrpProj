import hashlib
import os
from datetime import datetime

from core.config import SINGAPORE_TZ


def now_dt() -> datetime:
    return datetime.now(SINGAPORE_TZ)


def hash_value(value: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", value.encode("utf-8"), salt.encode("utf-8"), 120_000
    ).hex()


def make_salt() -> str:
    return os.urandom(16).hex()
