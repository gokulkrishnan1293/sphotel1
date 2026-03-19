"""Print template configuration schema."""
from __future__ import annotations

from pydantic import BaseModel, Field


class PrintTemplateConfig(BaseModel):
    restaurant_name: str = ""
    address_line_1: str = ""
    address_line_2: str = ""
    phone: str = ""
    gst_number: str = ""
    fssai_number: str = ""
    footer_message: str = "Thanks"
    show_name_field: bool = True
    show_cashier: bool = True
    show_token_no: bool = True
    show_bill_no: bool = True
    receipt_width: int = Field(default=42, ge=24, le=60)
    kot_width: int = Field(default=32, ge=24, le=60)


class PrintTemplateUpdate(BaseModel):
    restaurant_name: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    phone: str | None = None
    gst_number: str | None = None
    fssai_number: str | None = None
    footer_message: str | None = None
    show_name_field: bool | None = None
    show_cashier: bool | None = None
    show_token_no: bool | None = None
    show_bill_no: bool | None = None
    receipt_width: int | None = Field(default=None, ge=24, le=60)
    kot_width: int | None = Field(default=None, ge=24, le=60)
