from typing import TypedDict

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FeatureFlagsDict(TypedDict):
    """Internal typed dict for feature flags — used by service and repo layer."""

    waiter_mode: bool
    suggestion_engine: bool
    telegram_alerts: bool
    gst_module: bool
    payroll_rewards: bool
    discount_complimentary: bool
    waiter_transfer: bool
    bill_close_ux: bool


DEFAULT_FLAGS: FeatureFlagsDict = {
    "waiter_mode": False,
    "suggestion_engine": False,
    "telegram_alerts": False,
    "gst_module": False,
    "payroll_rewards": False,
    "discount_complimentary": False,
    "waiter_transfer": False,
    "bill_close_ux": False,
}


class FeatureFlagsResponse(BaseModel):
    """API response model for feature flags — serializes to camelCase JSON."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    waiter_mode: bool = False
    suggestion_engine: bool = False
    telegram_alerts: bool = False
    gst_module: bool = False
    payroll_rewards: bool = False
    discount_complimentary: bool = False
    waiter_transfer: bool = False
    bill_close_ux: bool = False
