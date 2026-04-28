from app.core.security import hash_password, verify_password, create_access_token
from jose import jwt
from app.core.config import settings

def test_hash_password_returns_hash():
    hashed = hash_password("mysecret")
    assert hashed != "mysecret"
    assert len(hashed) > 0

def test_verify_password_correct():
    hashed = hash_password("mysecret")
    assert verify_password("mysecret", hashed) is True

def test_verify_password_wrong():
    hashed = hash_password("mysecret")
    assert verify_password("wrongpass", hashed) is False

def test_hash_is_unique():
    h1 = hash_password("same")
    h2 = hash_password("same")
    assert h1 != h2  # bcrypt uses random salt

def test_create_access_token_contains_sub():
    token = create_access_token({"sub": "user@example.com"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "user@example.com"

def test_create_access_token_has_expiry():
    token = create_access_token({"sub": "user@example.com"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert "exp" in payload
