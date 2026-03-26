from fastapi import APIRouter

from app.api.v1.routes import (
    analytics,
    auth,
    custom_reports,
    fixed_report_configs,
    keyboard_shortcuts,
    telegram,
    bill_actions,
    bill_items,
    bills,
    expenses,
    gst,
    health,
    kot,
    kot_actions,
    menu,
    online_vendors,
    payments,
    print_agents,
    print_jobs,
    sections,
    staff,
    staff_actions,
    staff_admin,
    super_admin,
    table_layouts,
    tables,
    tenants,
    users,
    reports,
    public,
)

api_router = APIRouter()

# Health — no prefix; resolves to /api/v1/health
api_router.include_router(health.router)

# Resource domain routers — each declares its own prefix
api_router.include_router(auth.router)
api_router.include_router(bills.router)
api_router.include_router(bill_actions.router)
api_router.include_router(bill_items.router)
api_router.include_router(kot.router)
api_router.include_router(kot_actions.router)
api_router.include_router(payments.router)
api_router.include_router(print_jobs.router)
api_router.include_router(print_agents.router)
api_router.include_router(online_vendors.router)
api_router.include_router(menu.router)
api_router.include_router(staff.router)
api_router.include_router(staff_actions.router)
api_router.include_router(staff_admin.router)
api_router.include_router(expenses.router)
api_router.include_router(analytics.router)
api_router.include_router(custom_reports.router)
api_router.include_router(fixed_report_configs.router)
api_router.include_router(gst.router)
api_router.include_router(sections.router)
api_router.include_router(table_layouts.router)
api_router.include_router(tables.router)
api_router.include_router(tenants.router)
api_router.include_router(super_admin.router)
api_router.include_router(users.router)
api_router.include_router(telegram.router)
api_router.include_router(keyboard_shortcuts.router)
api_router.include_router(reports.router)
api_router.include_router(public.router)
