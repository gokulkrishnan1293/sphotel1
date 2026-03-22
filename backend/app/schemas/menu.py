import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.core.security.permissions import FoodType


class VendorPrice(BaseModel):
    vendor_slug: str
    price_paise: int

    model_config = {"from_attributes": True}


class MenuVariant(BaseModel):
    id: Optional[uuid.UUID] = None
    name: str
    price_paise: int
    parcel_price_paise: Optional[int] = None
    vendor_prices: list[VendorPrice] = []
    effective_price_paise: Optional[int] = None

    model_config = {"from_attributes": True}


class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    short_code: Optional[int] = Field(None, ge=1, le=9999)
    price_paise: int = Field(0, ge=0)
    food_type: FoodType = FoodType.VEG
    description: Optional[str] = Field(None, max_length=500)
    is_available: bool = True
    display_order: int = 0
    parcel_price_paise: Optional[int] = Field(None, ge=0)
    variants: list[MenuVariant] = []
    vendor_prices: list[VendorPrice] = []


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    short_code: Optional[int] = Field(None, ge=1, le=9999)
    price_paise: Optional[int] = Field(None, ge=0)
    food_type: Optional[FoodType] = None
    description: Optional[str] = Field(None, max_length=500)
    is_available: Optional[bool] = None
    display_order: Optional[int] = None
    parcel_price_paise: Optional[int] = Field(None, ge=0)
    variants: Optional[list[MenuVariant]] = None
    vendor_prices: Optional[list[VendorPrice]] = None


class MenuItemResponse(BaseModel):
    id: uuid.UUID
    tenant_id: str
    name: str
    category: str
    short_code: Optional[int]
    price_paise: int
    food_type: FoodType
    description: Optional[str]
    is_available: bool
    display_order: int
    parcel_price_paise: Optional[int] = None
    variants: list[MenuVariant] = []
    vendor_prices: list[VendorPrice] = []
    effective_price_paise: Optional[int] = None

    model_config = {"from_attributes": True}


class CategoryResponse(BaseModel):
    name: str
    item_count: int


class CategoryRename(BaseModel):
    new_name: str = Field(..., min_length=1, max_length=100)
