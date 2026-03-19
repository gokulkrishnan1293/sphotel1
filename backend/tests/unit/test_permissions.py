from app.core.security.permissions import (
    ROLE_DATA_SCOPE,
    ROLE_HIERARCHY,
    ROLE_PERMISSIONS,
    UserRole,
    can_assign_role,
)


def test_user_role_has_six_members() -> None:
    assert len(UserRole) == 6


def test_user_role_string_values() -> None:
    assert UserRole.BILLER == "biller"
    assert UserRole.WAITER == "waiter"
    assert UserRole.KITCHEN_STAFF == "kitchen_staff"
    assert UserRole.MANAGER == "manager"
    assert UserRole.ADMIN == "admin"
    assert UserRole.SUPER_ADMIN == "super_admin"


def test_role_permissions_covers_all_roles() -> None:
    for role in UserRole:
        assert role in ROLE_PERMISSIONS, f"Missing permissions for {role}"


def test_role_hierarchy_covers_all_roles() -> None:
    for role in UserRole:
        assert role in ROLE_HIERARCHY, f"Missing hierarchy for {role}"


def test_role_data_scope_covers_all_roles() -> None:
    for role in UserRole:
        assert role in ROLE_DATA_SCOPE, f"Missing data scope for {role}"


def test_can_assign_role_admin_to_manager() -> None:
    assert can_assign_role(UserRole.ADMIN, UserRole.MANAGER) is True


def test_can_assign_role_admin_to_biller() -> None:
    assert can_assign_role(UserRole.ADMIN, UserRole.BILLER) is True


def test_can_assign_role_admin_to_admin_is_false() -> None:
    # Cannot assign equal level
    assert can_assign_role(UserRole.ADMIN, UserRole.ADMIN) is False


def test_can_assign_role_admin_to_super_admin_is_false() -> None:
    # Cannot assign higher level
    assert can_assign_role(UserRole.ADMIN, UserRole.SUPER_ADMIN) is False


def test_can_assign_role_manager_to_biller() -> None:
    assert can_assign_role(UserRole.MANAGER, UserRole.BILLER) is True


def test_can_assign_role_biller_to_waiter_is_false() -> None:
    # Same hierarchy level — not strictly greater
    assert can_assign_role(UserRole.BILLER, UserRole.WAITER) is False


def test_can_assign_role_biller_to_manager_is_false() -> None:
    assert can_assign_role(UserRole.BILLER, UserRole.MANAGER) is False


def test_super_admin_can_assign_admin() -> None:
    assert can_assign_role(UserRole.SUPER_ADMIN, UserRole.ADMIN) is True


def test_super_admin_cannot_assign_super_admin() -> None:
    assert can_assign_role(UserRole.SUPER_ADMIN, UserRole.SUPER_ADMIN) is False
