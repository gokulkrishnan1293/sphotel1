import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.bill_enums import BillStatus, BillType, ItemStatus, PaymentMethod
from app.core.security.permissions import FoodType


class BillItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    menu_item_id: uuid.UUID | None
    name: str
    category: str
    price_paise: int
    override_price_paise: int | None = None
    food_type: FoodType
    quantity: int
    status: ItemStatus
    kot_ticket_id: uuid.UUID | None
    notes: str | None


class KotTicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ticket_number: int
    fired_at: datetime
    item_ids: list[uuid.UUID] = []


class BillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    bill_number: int | None
    bill_type: BillType
    status: BillStatus
    table_id: uuid.UUID | None
    covers: int | None
    reference_no: str | None
    platform: str | None
    subtotal_paise: int
    discount_paise: int
    gst_paise: int
    total_paise: int
    payment_method: PaymentMethod | None
    paid_at: datetime | None
    notes: str | None
    created_by: uuid.UUID
    created_by_name: str | None = None
    waiter_id: uuid.UUID | None
    waiter_name: str | None = None
    created_at: datetime
    updated_at: datetime
    items: list[BillItemResponse] = []
    kot_tickets: list[KotTicketResponse] = []


class BillSummaryResponse(BaseModel):
    """Lightweight bill for the active-bills panel (no items/KOTs)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    bill_number: int | None
    bill_type: BillType
    status: BillStatus
    table_id: uuid.UUID | None
    covers: int | None
    reference_no: str | None
    platform: str | None
    total_paise: int
    created_by: uuid.UUID
    waiter_id: uuid.UUID | None
    waiter_name: str | None = None
    item_names: list[str] = []
    created_at: datetime
    updated_at: datetime
