import enum
from typing import Final


class FoodType(enum.StrEnum):
    """Food classification for menu items."""

    VEG = "veg"
    EGG = "egg"
    NON_VEG = "non_veg"


class UserRole(enum.StrEnum):
    """Six roles with non-overlapping capability boundaries (FR32)."""

    BILLER = "biller"
    WAITER = "waiter"
    KITCHEN_STAFF = "kitchen_staff"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Authorization level — used for role assignment guard (FR87).
# A user may only assign roles with a level STRICTLY LESS than their own.
ROLE_HIERARCHY: Final[dict[UserRole, int]] = {
    UserRole.BILLER: 1,
    UserRole.WAITER: 1,
    UserRole.KITCHEN_STAFF: 1,
    UserRole.MANAGER: 2,
    UserRole.ADMIN: 3,
    UserRole.SUPER_ADMIN: 4,
}

# Explicit capability sets per role — single source of truth (FR32, FR89).
# Endpoints declare allowed roles via require_role(); never hardcode per handler.
ROLE_PERMISSIONS: Final[dict[UserRole, frozenset[str]]] = {
    UserRole.BILLER: frozenset({
        "bills:create", "bills:read_own", "bills:modify_own",
        "kot:fire", "payments:collect", "menu:read",
        "print:trigger", "templates:use",
    }),
    UserRole.WAITER: frozenset({
        "bills:create", "bills:read_own", "kot:fire",
        "menu:read", "bills:transfer",
    }),
    UserRole.KITCHEN_STAFF: frozenset({
        "kot:read", "kot:mark_ready", "menu:toggle_availability",
    }),
    UserRole.MANAGER: frozenset({
        "bills:read", "staff:attendance", "payroll:view",
        "expenses:record", "kot:read", "menu:read", "shifts:manage",
    }),
    UserRole.ADMIN: frozenset({
        "bills:read", "bills:void_approve", "bills:audit",
        "menu:manage", "staff:manage", "payroll:manage",
        "expenses:manage", "reports:view", "settings:manage",
        "print_agents:manage", "telegram:configure", "gst:report",
        "feature_flags:read",
    }),
    UserRole.SUPER_ADMIN: frozenset({
        "tenants:manage", "platform:analytics",
    }),
}

# Data visibility scope per role (FR89).
# Repositories use this to scope queries — enforced structurally, not in handlers.
# Values: "own_session" | "tenant_staff" | "full_tenant" | "platform"
ROLE_DATA_SCOPE: Final[dict[UserRole, str]] = {
    UserRole.BILLER: "own_session",
    UserRole.WAITER: "own_session",
    UserRole.KITCHEN_STAFF: "full_tenant",
    UserRole.MANAGER: "tenant_staff",
    UserRole.ADMIN: "full_tenant",
    UserRole.SUPER_ADMIN: "platform",
}


def can_assign_role(assigner: UserRole, target: UserRole) -> bool:
    """Return True only if assigner's level is strictly greater than target's.

    Implements FR87: no user can grant a role at or above their own level.
    Admin (3) can assign Manager (2) or below.
    Admin (3) cannot assign Admin (3) or Super-Admin (4).
    """
    return ROLE_HIERARCHY[assigner] > ROLE_HIERARCHY[target]
