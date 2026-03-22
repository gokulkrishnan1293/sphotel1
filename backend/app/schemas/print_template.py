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
    receipt_font_size: int = Field(default=1, ge=1, le=8)
    kot_font_size: int = Field(default=1, ge=1, le=8)
    top_padding: int = Field(default=2, ge=0, le=10)
    bottom_padding: int = Field(default=5, ge=0, le=15)
    eod_show_payment: bool = True
    eod_show_items: bool = True
    eod_show_waiters: bool = True
    eod_font_size: int = Field(default=1, ge=1, le=8)
    bold_header: bool = False
    bold_total: bool = False
    bold_kot_number: bool = False
    bold_kot_items: bool = False
    bold_eod_headers: bool = False


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
    receipt_font_size: int | None = Field(default=None, ge=1, le=8)
    kot_font_size: int | None = Field(default=None, ge=1, le=8)
    top_padding: int | None = Field(default=None, ge=0, le=10)
    bottom_padding: int | None = Field(default=None, ge=0, le=15)
    eod_show_payment: bool | None = None
    eod_show_items: bool | None = None
    eod_show_waiters: bool | None = None
    eod_font_size: int | None = Field(default=None, ge=1, le=8)
    bold_header: bool | None = None
    bold_total: bool | None = None
    bold_kot_number: bool | None = None
    bold_kot_items: bool | None = None
    bold_eod_headers: bool | None = None
