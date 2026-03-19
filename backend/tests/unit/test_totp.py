import base64

import pyotp

from app.core.security.totp import (
    generate_totp_secret,
    get_provisioning_uri,
    verify_totp,
)


def test_generate_totp_secret_returns_base32_string() -> None:
    secret = generate_totp_secret()
    assert isinstance(secret, str)
    assert len(secret) >= 16
    base64.b32decode(secret)  # raises ValueError if not valid base32


def test_get_provisioning_uri_format() -> None:
    secret = generate_totp_secret()
    uri = get_provisioning_uri(secret, "admin@hotel.com")
    assert uri.startswith("otpauth://totp/")


def test_get_provisioning_uri_contains_issuer_and_email() -> None:
    secret = generate_totp_secret()
    uri = get_provisioning_uri(secret, "admin@hotel.com", issuer="sphotel")
    assert "sphotel" in uri
    assert "admin" in uri
    assert "hotel.com" in uri


def test_verify_totp_correct_code_returns_true() -> None:
    secret = generate_totp_secret()
    current_code = pyotp.TOTP(secret).now()
    assert verify_totp(secret, current_code) is True


def test_verify_totp_wrong_code_returns_false() -> None:
    secret = generate_totp_secret()
    assert verify_totp(secret, "000000") is False
