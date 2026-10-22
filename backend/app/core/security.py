import base64
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings

hasher = PasswordHasher()
bearer_scheme = HTTPBearer(auto_error=False)


def _get_fernet() -> Fernet:
    """Return a Fernet cipher instance using the configured secret."""
    key = settings.APP_ENCRYPTION_KEY.strip()
    if not key:
        raise ValueError("APP_ENCRYPTION_KEY is not configured")
    try:
        return Fernet(key.encode())
    except Exception as e:
        raise ValueError(f"Invalid APP_ENCRYPTION_KEY: {e}")



def hash_password(password: str) -> str:
    """Hash a password using argon2-cffi."""
    return hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify an argon2 hashed password."""
    try:
        return hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, Exception):
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a signed JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "TOKEN_EXPIRED", "message": "Token has expired"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid authentication token"}
        )


def encrypt_api_key(plain_key: str) -> str:
    """Encrypt a user-provided API key using Fernet."""
    if not plain_key:
        return ""
    fernet = _get_fernet()
    encrypted = fernet.encrypt(plain_key.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an encrypted API key."""
    if not encrypted_key:
        return ""
    fernet = _get_fernet()
    try:
        decrypted = fernet.decrypt(encrypted_key.encode("utf-8"))
        return decrypted.decode("utf-8")
    except Exception:
        return ""


def mask_api_key(plain_or_encrypted: str, is_encrypted: bool = False) -> str:
    """Mask an API key showing only the last 4 characters."""
    raw = decrypt_api_key(plain_or_encrypted) if is_encrypted else plain_or_encrypted
    if not raw:
        return ""
    if len(raw) <= 6:
        return "••••"
    return f"{raw[:3]}••••{raw[-4:]}"
