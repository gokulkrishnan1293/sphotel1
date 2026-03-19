import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import jwt
import pytest

from app.core.security.jwt import create_access_token, decode_access_token
from app.core.security.permissions import UserRole


def _make_token(role: UserRole = UserRole.BILLER) -> str:
    return create_access_token(
        user_id=uuid.uuid4(),
        tenant_id="tenant-abc",
        role=role,
    )


def test_create_access_token_returns_string() -> None:
    token = _make_token()
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token_returns_correct_payload() -> None:
    uid = uuid.uuid4()
    token = create_access_token(uid, "tenant-xyz", UserRole.MANAGER)
    payload = decode_access_token(token)
    assert payload["user_id"] == str(uid)
    assert payload["tenant_id"] == "tenant-xyz"
    assert payload["role"] == "manager"
    assert "iat" in payload
    assert "exp" in payload


def test_expired_token_raises_invalid_token_error() -> None:
    uid = uuid.uuid4()
    past = datetime.now(UTC) - timedelta(hours=5)
    with patch("app.core.security.jwt.datetime") as mock_dt:
        mock_dt.now.return_value = past
        token = create_access_token(uid, "t", UserRole.BILLER)
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


def test_tampered_token_raises_invalid_token_error() -> None:
    token = _make_token()
    tampered = token[:-4] + "XXXX"
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(tampered)
