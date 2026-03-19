from app.schemas.feature_flags import (
    DEFAULT_FLAGS,
    FeatureFlagsDict,
    FeatureFlagsResponse,
)


def test_default_flags_all_false() -> None:
    """DEFAULT_FLAGS must have all seven flags set to False."""
    assert DEFAULT_FLAGS["waiter_mode"] is False
    assert DEFAULT_FLAGS["suggestion_engine"] is False
    assert DEFAULT_FLAGS["telegram_alerts"] is False
    assert DEFAULT_FLAGS["gst_module"] is False
    assert DEFAULT_FLAGS["payroll_rewards"] is False
    assert DEFAULT_FLAGS["discount_complimentary"] is False
    assert DEFAULT_FLAGS["waiter_transfer"] is False


def test_default_flags_has_all_keys() -> None:
    """DEFAULT_FLAGS must contain exactly the seven expected keys."""
    expected = {
        "waiter_mode",
        "suggestion_engine",
        "telegram_alerts",
        "gst_module",
        "payroll_rewards",
        "discount_complimentary",
        "waiter_transfer",
    }
    assert set(DEFAULT_FLAGS.keys()) == expected


def test_feature_flags_response_default_all_false() -> None:
    """FeatureFlagsResponse must default all flags to False."""
    response = FeatureFlagsResponse()
    assert response.waiter_mode is False
    assert response.suggestion_engine is False


def test_feature_flags_response_serializes_camel_case() -> None:
    """FeatureFlagsResponse must serialize to camelCase JSON keys."""
    flags = FeatureFlagsDict(
        waiter_mode=True,
        suggestion_engine=False,
        telegram_alerts=True,
        gst_module=False,
        payroll_rewards=True,
        discount_complimentary=False,
        waiter_transfer=True,
    )
    response = FeatureFlagsResponse(**flags)
    serialized = response.model_dump(by_alias=True)
    assert serialized["waiterMode"] is True
    assert serialized["suggestionEngine"] is False
    assert serialized["telegramAlerts"] is True
    assert serialized["gstModule"] is False
    assert serialized["payrollRewards"] is True
    assert serialized["discountComplimentary"] is False
    assert serialized["waiterTransfer"] is True


def test_feature_flags_response_snake_case_fields_accessible() -> None:
    """FeatureFlagsResponse must allow access via snake_case attribute names."""
    response = FeatureFlagsResponse(waiter_mode=True)
    assert response.waiter_mode is True


def test_feature_flags_response_constructed_from_dict() -> None:
    """FeatureFlagsResponse must accept **FeatureFlagsDict unpacking."""
    flags = FeatureFlagsDict(
        waiter_mode=True,
        suggestion_engine=True,
        telegram_alerts=False,
        gst_module=False,
        payroll_rewards=False,
        discount_complimentary=False,
        waiter_transfer=False,
    )
    response = FeatureFlagsResponse(**flags)
    assert response.waiter_mode is True
    assert response.suggestion_engine is True
    assert response.telegram_alerts is False
