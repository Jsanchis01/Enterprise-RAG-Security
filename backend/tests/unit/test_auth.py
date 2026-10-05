from datetime import timedelta
import pytest
import jwt
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.core.config import get_settings

settings = get_settings()


def test_argon2_password_hashing():
    raw_password = "SuperSecurePassword#2026"
    hashed = hash_password(raw_password)

    assert hashed != raw_password
    assert hashed.startswith("$argon2id$")
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_lifecycle():
    payload = {
        "sub": "b2f63f3c-83b3-46ea-9d89-6e3e5c9a7f31",
        "username": "researcher",
        "role": "analyst",
        "clearance_level": 3,
        "department": "finance",
    }
    token = create_access_token(payload, expires_delta=timedelta(minutes=15))
    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    decoded = decode_access_token(token)
    assert decoded["sub"] == payload["sub"]
    assert decoded["username"] == payload["username"]
    assert decoded["role"] == payload["role"]
    assert decoded["clearance_level"] == 3
    assert decoded["department"] == "finance"
    assert "exp" in decoded


def test_jwt_expired_token():
    payload = {"sub": "expired_user", "username": "expired"}
    # Generate token already expired 5 minutes ago
    token = create_access_token(payload, expires_delta=timedelta(minutes=-5))

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_jwt_tampered_signature():
    payload = {"sub": "tampered_user", "role": "admin"}
    token = create_access_token(payload)

    # Tamper with the secret key signature
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, "wrong_secret_key_32_characters_long_!", algorithms=[settings.ALGORITHM])
