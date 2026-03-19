from app.core.security.pin import hash_pin, verify_pin


def test_hash_pin_returns_bcrypt_string() -> None:
    result = hash_pin("1234")
    assert result.startswith("$2b$")


def test_verify_pin_correct_returns_true() -> None:
    pin_hash = hash_pin("5678")
    assert verify_pin("5678", pin_hash) is True


def test_verify_pin_wrong_returns_false() -> None:
    pin_hash = hash_pin("1234")
    assert verify_pin("9999", pin_hash) is False


def test_hash_pin_different_salts() -> None:
    h1 = hash_pin("1234")
    h2 = hash_pin("1234")
    assert h1 != h2  # bcrypt salts are unique per call
