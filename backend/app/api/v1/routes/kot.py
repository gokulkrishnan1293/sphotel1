import uuid
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.models.bill import Bill
from app.models.bill_enums import BillStatus, BillType
from app.models.kot import BillItem, KotTicket
from app.models.table import TableLayout
from app.schemas.common import DataResponse
from app.schemas.kot_responses import ActiveKotView, KotItemView

router = APIRouter(prefix="/kot", tags=["kot"])

_OPEN = {BillStatus.DRAFT, BillStatus.KOT_SENT, BillStatus.PARTIALLY_SENT}
_ALLOWED = require_role(
    UserRole.KITCHEN_STAFF, UserRole.BILLER, UserRole.MANAGER,
    UserRole.ADMIN, UserRole.SUPER_ADMIN,
)


def _bill_label(bill: Bill, table_names: dict[uuid.UUID, str]) -> str:
    if bill.bill_type == BillType.TABLE:
        return table_names.get(bill.table_id, "Table")  # type: ignore[arg-type]
    if bill.bill_type == BillType.ONLINE:
        return f"{bill.platform or 'Online'} #{bill.reference_no or '—'}"
    return "Parcel"


@router.get("/active", response_model=DataResponse[list[ActiveKotView]])
async def list_active_kots(
    user: CurrentUser = Depends(_ALLOWED),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[ActiveKotView]]:
    tid = user["tenant_id"]

    bills_res = await db.execute(
        select(Bill).where(Bill.tenant_id == tid, Bill.status.in_(_OPEN))
    )
    bills = bills_res.scalars().all()
    bill_map = {b.id: b for b in bills}
    if not bill_map:
        return DataResponse(data=[])

    bill_ids = list(bill_map.keys())

    table_ids = [b.table_id for b in bills if b.table_id]
    table_names: dict[uuid.UUID, str] = {}
    if table_ids:
        tbl_res = await db.execute(
            select(TableLayout).where(TableLayout.id.in_(table_ids))
        )
        table_names = {t.id: t.name for t in tbl_res.scalars().all()}

    kots_res = await db.execute(
        select(KotTicket)
        .where(KotTicket.bill_id.in_(bill_ids), KotTicket.ready_at.is_(None))
        .order_by(KotTicket.fired_at.desc())
    )
    kots = kots_res.scalars().all()
    kot_map = {k.id: k for k in kots}
    if not kot_map:
        return DataResponse(data=[])

    items_res = await db.execute(
        select(BillItem).where(BillItem.kot_ticket_id.in_(list(kot_map.keys())))
    )
    items_by_kot: dict[uuid.UUID, list[BillItem]] = {}
    for item in items_res.scalars().all():
        if item.kot_ticket_id:
            items_by_kot.setdefault(item.kot_ticket_id, []).append(item)

    views: list[ActiveKotView] = []
    for kot in kots:
        bill = bill_map.get(kot.bill_id)
        if not bill:
            continue
        kot_items = [
            KotItemView(item_id=i.id, name=i.name, quantity=i.quantity, food_type=i.food_type)
            for i in items_by_kot.get(kot.id, [])
        ]
        views.append(ActiveKotView(
            id=kot.id,
            ticket_number=kot.ticket_number,
            fired_at=kot.fired_at,
            bill_id=kot.bill_id,
            bill_label=_bill_label(bill, table_names),
            items=kot_items,
            ready_item_ids=[uuid.UUID(x) for x in (kot.ready_item_ids or [])],
        ))

    return DataResponse(data=views)
