import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.core.security.permissions import UserRole


class PinLoginRequest(BaseModel):
    user_id: uuid.UUID
    pin: str = Field(min_length=4, max_length=8)
    tenant_slug: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    message: str


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    tenant_slug: str | None = None
    remember_me: bool = False


class TotpSetupRequest(BaseModel):
    email: EmailStr
    password: str


class TotpSetupResponse(BaseModel):
    provisioning_uri: str
    secret: str


class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: uuid.UUID = Field(validation_alias="id")
    tenant_id: str
    name: str
    role: UserRole
    email: str | None
    is_active: bool
    preferences: dict[str, object]


class UpdateCredentialsRequest(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UpdateCredentialsRequest":
        if self.email is None and self.password is None:
            raise ValueError("At least one of email or password must be provided")
        return self


class AdminResetRequest(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "AdminResetRequest":
        if self.email is None and self.password is None:
            raise ValueError("At least one of email or password must be provided")
        return self


class TenantPublicInfo(BaseModel):
    id: str
    name: str
    slug: str
    pwa_settings: dict | None = None
    logo_path: str | None = None


class StaffPublicItem(BaseModel):
    id: str
    name: str
    role: str
