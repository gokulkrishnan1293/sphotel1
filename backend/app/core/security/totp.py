import pyotp


def generate_totp_secret() -> str:
    """Generate a new random base32 TOTP secret."""
    return pyotp.random_base32()


def get_provisioning_uri(
    secret: str,
    email: str,
    issuer: str = "sphotel",
) -> str:
    """Return an otpauth:// URI for authenticator app enrollment."""
    return pyotp.TOTP(secret).provisioning_uri(email, issuer_name=issuer)


def verify_totp(secret: str, code: str) -> bool:
    """Return True if code is valid for the current or adjacent 30s window."""
    return bool(pyotp.TOTP(secret).verify(code, valid_window=1))
