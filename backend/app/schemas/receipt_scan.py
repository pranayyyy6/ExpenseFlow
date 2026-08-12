from pydantic import BaseModel
from typing import Optional


class ReceiptItemParsed(BaseModel):
    item_name: str
    quantity: int = 1
    price: float
    total: float


class ReceiptParsed(BaseModel):
    store_name: Optional[str] = None
    receipt_date: Optional[str] = None
    total_amount: Optional[float] = None
    items: list[ReceiptItemParsed] = []