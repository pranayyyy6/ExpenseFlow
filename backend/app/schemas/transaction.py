from typing import Optional

from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    transaction_type: str
    amount: float
    category: Optional[str] = None
    description: Optional[str] = None
    merchant: Optional[str] = None
    transaction_date: Optional[str] = None
    payment_method: Optional[str] = None
    reference_id: Optional[str] = None


class TransactionUpdate(BaseModel):
    transaction_type: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    merchant: Optional[str] = None
    transaction_date: Optional[str] = None
    payment_method: Optional[str] = None
    reference_id: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    transaction_type: str
    amount: float
    category: Optional[str]
    description: Optional[str]
    merchant: Optional[str]
    transaction_date: Optional[str]
    payment_method: Optional[str]
    reference_id: Optional[str]

    model_config = ConfigDict(from_attributes=True)