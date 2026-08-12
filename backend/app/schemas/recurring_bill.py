from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RecurringBillCreate(BaseModel):
    name: str
    amount: float
    frequency: str
    next_due_date: str
    category: str = "Bills"
    payment_method: str | None = None
    auto_pay: bool = False


class RecurringBillUpdate(BaseModel):
    name: str | None = None
    amount: float | None = None
    frequency: str | None = None
    next_due_date: str | None = None
    category: str | None = None
    payment_method: str | None = None
    auto_pay: bool | None = None
    is_active: bool | None = None


class RecurringBillResponse(BaseModel):
    id: int
    name: str
    amount: float
    frequency: str
    next_due_date: str
    category: str
    payment_method: str | None
    auto_pay: bool
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )