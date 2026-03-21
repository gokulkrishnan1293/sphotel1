import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{1,61}[a-z0-9]$")
_RESERVED_SLUGS: frozenset[str] = frozenset(
    {"admin", "api", "www", "app", "static", "assets", "mail", "help", "support"}
)


class TenantCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    subdomain: str = Field(min_length=3, max_length=63)

    @field_validator("subdomain")
    @classmethod
    def validate_subdomain(cls, v: str) -> str:
        slug = v.lower()
        if not _SLUG_RE.match(slug):
            raise ValueError(
                "Subdomain must be 3–63 chars, lowercase letters/digits/hyphens,"
                " not starting or ending with a hyphen"
            )
        if slug in _RESERVED_SLUGS:
            raise ValueError(f"'{slug}' is a reserved subdomain")
        return slug


class PWASettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    app_name: str | None = None
    app_short_name: str | None = None


class BrandingUpdateRequest(BaseModel):
    pwa_settings: PWASettings | None = None


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    is_active: bool
    onboarding_completed: bool
    created_at: datetime
    pwa_settings: PWASettings | None = None
    logo_path: str | None = None


class PlatformStatsResponse(BaseModel):
    total_tenants: int
    total_bills_processed: int  # Always 0 until Epic 4 creates bills table


class ChecklistItem(BaseModel):
    key: str
    label: str
    completed: bool
    route: str  # Frontend URL path — e.g. "/admin/staff"


class OnboardingStatusResponse(BaseModel):
    completed: bool
    items: list[ChecklistItem]
