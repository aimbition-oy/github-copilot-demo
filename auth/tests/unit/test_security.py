"""Unit tests for app/security.py."""

import jwt
import pytest

from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

SECRET = "unit-test-secret"


class TestPasswordHashing:
    def test_hash_differs_from_plain(self):
        hashed = hash_password("mysecret")
        assert hashed != "mysecret"

    def test_verify_correct_password(self):
        hashed = hash_password("correcthorsebattery")
        assert verify_password("correcthorsebattery", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correcthorsebattery")
        assert verify_password("wrongpassword", hashed) is False


class TestJWT:
    def test_create_and_decode_roundtrip(self):
        token = create_access_token(user_id=42, username="alice", secret=SECRET)
        payload = decode_access_token(token, SECRET)
        assert payload["sub"] == "42"
        assert payload["username"] == "alice"

    def test_expired_token_raises(self):
        token = create_access_token(user_id=1, username="bob", secret=SECRET, expire_hours=-1)
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_access_token(token, SECRET)

    def test_tampered_token_raises(self):
        token = create_access_token(user_id=1, username="carol", secret=SECRET)
        # Flip the last character to tamper with the signature
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        with pytest.raises(jwt.InvalidTokenError):
            decode_access_token(tampered, SECRET)

    def test_wrong_secret_raises(self):
        token = create_access_token(user_id=1, username="dave", secret=SECRET)
        with pytest.raises(jwt.InvalidSignatureError):
            decode_access_token(token, "wrong-secret")
