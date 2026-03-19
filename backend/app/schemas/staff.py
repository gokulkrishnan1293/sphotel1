import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.security.permissions import UserRole


class CreateStaffRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    role: UserRole
    pin: str = Field(min_length=4, max_length=8)
    short_code: int | None = Field(None, ge=1, le=999)


class UpdateStaffRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    role: UserRole | None = None
    is_active: bool | None = None
    short_code: int | None = Field(None, ge=1, le=999)


class ResetPinRequest(BaseModel):
    pin: str = Field(min_length=4, max_length=8)


class StaffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: str
    name: str
    role: UserRole
    short_code: int | None
    is_active: bool
    created_at: datetime


class CreateAdminRequest(BaseModel):
    tenant_slug: str = Field(min_length=1, max_length=63)
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)


class AdminCreatedResponse(StaffResponse):
    totp_uri: str


class WaiterView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    short_code: int | None
