"""
Tests for password hashing: get_password_hash(plain, salt) and verify_password(plain, salt, hashed).
"""

from app.utils.security import get_password_hash, verify_password


def _salt() -> str:
    return "a1b2c3d4e5f6"  # fixed salt for deterministic tests where needed


def test_get_password_hash_returns_non_empty_string() -> None:
    hashed = get_password_hash("mysecret", _salt())
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    assert hashed != "mysecret"


def test_get_password_hash_different_each_time() -> None:
    """Same (salt+password) can produce different hashes (bcrypt's own salt); different user salt yields different hash."""
    salt1 = "salt1"
    salt2 = "salt2"
    h1 = get_password_hash("same", salt1)
    h2 = get_password_hash("same", salt1)
    h3 = get_password_hash("same", salt2)
    assert verify_password("same", salt1, h1) and verify_password("same", salt1, h2)
    assert h1 != h3


def test_verify_password_correct() -> None:
    plain = "correct-password"
    salt = _salt()
    hashed = get_password_hash(plain, salt)
    assert verify_password(plain, salt, hashed) is True


def test_verify_password_wrong_returns_false() -> None:
    salt = _salt()
    hashed = get_password_hash("real-password", salt)
    assert verify_password("wrong-password", salt, hashed) is False


def test_verify_password_wrong_salt_returns_false() -> None:
    hashed = get_password_hash("secret", "salt-a")
    assert verify_password("secret", "salt-b", hashed) is False


def test_verify_password_empty_plain() -> None:
    salt = _salt()
    hashed = get_password_hash("something", salt)
    assert verify_password("", salt, hashed) is False


def test_verify_password_empty_hash_returns_false() -> None:
    assert verify_password("any", "s", "") is False


def test_verify_password_legacy_no_salt() -> None:
    """Backward compat: salt=None uses empty string (legacy users without password_salt)."""
    hashed = get_password_hash("legacy", "")
    assert verify_password("legacy", None, hashed) is True
    assert verify_password("wrong", None, hashed) is False


def get_password_hash_for_dml() -> str:
    return get_password_hash("1070160286", "salt")
