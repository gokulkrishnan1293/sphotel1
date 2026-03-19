# Import all model modules so Base.metadata registers all tables.
# Alembic autogenerate reads Base.metadata — missing imports = missing tables.
from app.models import (
    audit_log,  # noqa: F401
    base,  # noqa: F401
    bill,  # noqa: F401
    custom_report,  # noqa: F401
    bill_enums,  # noqa: F401
    feature_flags,  # noqa: F401
    kot,  # noqa: F401
    menu,  # noqa: F401
    table,  # noqa: F401
    tenant,  # noqa: F401
    user,  # noqa: F401
)
