"""
Production-grade authentication primitives.

Replaces the previous mock JWT (prefix-check) and plaintext passwords with:
  - bcrypt password hashing (passlib)
  - signed JWTs with expiry (python-jose, HS256)

The signing secret comes from JWT_SECRET_KEY. In production (Azure App Service /
Key Vault) this MUST be set to a strong random value; a loud warning is printed if
the insecure development default is used.
"""

import os
import warnings
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError

JWT_ALGORITHM = "HS256"
TOKEN_TTL_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

_DEV_DEFAULT = "dev-only-insecure-secret-change-me"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", _DEV_DEFAULT)
if JWT_SECRET_KEY == _DEV_DEFAULT:
    warnings.warn(
        "JWT_SECRET_KEY is not set; using an insecure development default. "
        "Set JWT_SECRET_KEY (e.g. `python -c \"import secrets;print(secrets.token_hex(32))\"`) "
        "before any deployment.",
        stacklevel=2,
    )


# ---- passwords ----
def hash_password(plain: str) -> str:
    # bcrypt operates on <=72 bytes; truncate defensively.
    return bcrypt.hashpw(plain.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except Exception:
        return False


# ---- tokens ----
def create_access_token(claims: dict, ttl_minutes: int = TOKEN_TTL_MINUTES) -> str:
    to_encode = claims.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Return the token claims, or raise JWTError if invalid/expired."""
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
