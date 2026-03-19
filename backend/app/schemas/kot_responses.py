import uuid
from datetime import datetime
from pydantic import BaseModel
from app.core.security.permissions import FoodType


class KotItemView(BaseModel):
    item_id: uuid.UUID
    name: str
    quantity: int
    food_type: FoodType


class ActiveKotView(BaseModel):
    id: uuid.UUID
    ticket_number: int
    fired_at: datetime
    bill_id: uuid.UUID
    bill_label: str
    items: list[KotItemView]
    ready_item_ids: list[uuid.UUID] = []
