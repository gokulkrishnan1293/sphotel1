import bcrypt

_ROUNDS = 12  # cost factor — ~100ms on modern hardware


def hash_pin(pin: str) -> str:
    """Hash a plaintext PIN with bcrypt. Returns str for storage in DB."""
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt(rounds=_ROUNDS)).decode()


def verify_pin(pin: str, pin_hash: str) -> bool:
    """Return True if pin matches the stored bcrypt hash."""
    return bool(bcrypt.checkpw(pin.encode(), pin_hash.encode()))
