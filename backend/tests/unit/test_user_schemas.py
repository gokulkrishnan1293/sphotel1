"""Unit tests for user schemas added in Story 2.6."""
import pytest
from pydantic import ValidationError

from app.schemas.users import PreferencesUpdateRequest


def test_preferences_dark_valid() -> None:
    req = PreferencesUpdateRequest(theme="dark")
    assert req.theme == "dark"


def test_preferences_light_valid() -> None:
    req = PreferencesUpdateRequest(theme="light")
    assert req.theme == "light"


def test_preferences_high_contrast_valid() -> None:
    req = PreferencesUpdateRequest(theme="high_contrast")
    assert req.theme == "high_contrast"


def test_preferences_invalid_theme_raises() -> None:
    with pytest.raises(ValidationError):
        PreferencesUpdateRequest(theme="blue")  # type: ignore[arg-type]


def test_preferences_empty_raises() -> None:
    with pytest.raises(ValidationError):
        PreferencesUpdateRequest()  # type: ignore[call-arg]


def test_preferences_high_hyphen_raises() -> None:
    """high-contrast (hyphen) is not a valid value — must use underscore."""
    with pytest.raises(ValidationError):
        PreferencesUpdateRequest(theme="high-contrast")  # type: ignore[arg-type]
