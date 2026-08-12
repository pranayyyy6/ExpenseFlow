from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ============================================================
# RECEIPT ITEM
# ============================================================

class ReceiptItemResponse(BaseModel):

    id: int

    receipt_id: int

    item_name: str

    quantity: int

    price: float

    category: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# CREATE RECEIPT
# ============================================================

class ReceiptCreate(BaseModel):

    store_name: str

    receipt_date: str | None = None

    total_amount: float | None = None

    image_path: str | None = None


# ============================================================
# UPDATE RECEIPT
# ============================================================

class ReceiptUpdate(BaseModel):

    store_name: str | None = None

    receipt_date: str | None = None

    total_amount: float | None = None

    image_path: str | None = None


# ============================================================
# RECEIPT RESPONSE
# ============================================================

class ReceiptResponse(BaseModel):

    id: int

    store_name: str

    receipt_date: str | None = None

    total_amount: float | None = None

    image_path: str | None = None

    created_at: datetime

    items: list[ReceiptItemResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )