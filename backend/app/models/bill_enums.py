import enum

from sqlalchemy import Enum as SAEnum


class BillType(enum.StrEnum):
    TABLE = "table"
    PARCEL = "parcel"
    ONLINE = "online"


class BillStatus(enum.StrEnum):
    DRAFT = "draft"
    KOT_SENT = "kot_sent"
    PARTIALLY_SENT = "partially_sent"
    BILLED = "billed"
    VOID = "void"


class ItemStatus(enum.StrEnum):
    PENDING = "pending"
    SENT = "sent"
    VOIDED = "voided"


class PaymentMethod(enum.StrEnum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    ONLINE = "online"
    OTHER = "other"


def sa_enum(enum_cls: type[enum.StrEnum], name: str) -> SAEnum:
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=True,
        create_type=False,
        values_callable=lambda obj: [e.value for e in obj],
    )
