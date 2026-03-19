"""Shared response-building helpers for bill routes."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import TenantUser
from app.schemas.bill_responses import BillItemResponse, BillResponse, KotTicketResponse


def build_response(bill, items, kots, user_names: dict | None = None) -> BillResponse:  # type: ignore[no-untyped-def]
    kot_item_map: dict[uuid.UUID, list[uuid.UUID]] = {}
    for item in items:
        if item.kot_ticket_id:
            kot_item_map.setdefault(item.kot_ticket_id, []).append(item.id)
    names = user_names or {}
    return BillResponse(
        **{f: getattr(bill, f) for f in (
            "id", "bill_number", "bill_type", "status", "table_id", "covers", "reference_no", "platform",
            "subtotal_paise", "discount_paise", "gst_paise", "total_paise", "payment_method",
            "paid_at", "notes", "created_by", "waiter_id", "created_at", "updated_at",
        )},
        created_by_name=names.get(bill.created_by),
        waiter_name=names.get(bill.waiter_id) if bill.waiter_id else None,
        items=[BillItemResponse.model_validate(i) for i in items],
        kot_tickets=[
            KotTicketResponse(id=k.id, ticket_number=k.ticket_number,
                              fired_at=k.fired_at, item_ids=kot_item_map.get(k.id, []))
            for k in kots
        ],
    )


async def fetch_user_names(db: AsyncSession, tenant_id: str, *ids: uuid.UUID | None) -> dict[uuid.UUID, str]:
    valid = [i for i in ids if i is not None]
    if not valid:
        return {}
    rows = await db.execute(
        select(TenantUser.id, TenantUser.name).where(TenantUser.id.in_(valid), TenantUser.tenant_id == tenant_id)
    )
    return {r.id: r.name for r in rows}
