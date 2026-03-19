import uuid

from pydantic import BaseModel, ConfigDict


class SectionCreate(BaseModel):
    name: str
    color: str = "#3b82f6"
    position: int = 0


class SectionUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    position: int | None = None


class SectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    color: str
    position: int


class TableCreate(BaseModel):
    section_id: uuid.UUID
    name: str
    capacity: int = 4
    is_active: bool = True
    position: int = 0


class TableUpdate(BaseModel):
    name: str | None = None
    capacity: int | None = None
    is_active: bool | None = None
    position: int | None = None
    section_id: uuid.UUID | None = None


class TableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    section_id: uuid.UUID
    name: str
    capacity: int
    is_active: bool
    position: int


class SectionWithTablesResponse(SectionResponse):
    tables: list[TableResponse] = []
