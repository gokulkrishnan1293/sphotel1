from pydantic import BaseModel
import uuid

from app.models.bill_enums import BillType, PaymentMethod
from app.core.security.permissions import FoodType


class OpenBillRequest(BaseModel):
    bill_type: BillType
    table_id: uuid.UUID | None = None
    covers: int | None = None
    reference_no: str | None = None
    platform: str | None = None
    notes: str | None = None
    waiter_id: uuid.UUID | None = None


class AddItemRequest(BaseModel):
    menu_item_id: uuid.UUID | None = None
    name: str
    category: str
    price_paise: int
    food_type: FoodType = FoodType.VEG
    quantity: int = 1
    notes: str | None = None


class UpdateItemRequest(BaseModel):
    quantity: int | None = None
    notes: str | None = None
    override_price_paise: int | None = None


class CloseBillRequest(BaseModel):
    payment_method: PaymentMethod
    discount_paise: int = 0


class UpdatePaymentRequest(BaseModel):
    payment_method: PaymentMethod


class UpdateBillRequest(BaseModel):
    bill_type: BillType | None = None
    platform: str | None = None
    waiter_id: uuid.UUID | None = None
    table_id: uuid.UUID | None = None
    reference_no: str | None = None
