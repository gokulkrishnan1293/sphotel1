import uuid
from datetime import datetime
from pydantic import BaseModel


class CreatePrintJobRequest(BaseModel):
    bill_id: uuid.UUID
    job_type: str = "receipt"   # receipt | kot
    printer_name: str | None = None


class PrintJobStatusUpdate(BaseModel):
    status: str                  # done | failed
    error: str | None = None


class PrintJobResponse(BaseModel):
    id: uuid.UUID
    tenant_id: str
    bill_id: uuid.UUID | None
    job_type: str
    status: str
    payload: dict
    printer_name: str | None
    error: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
