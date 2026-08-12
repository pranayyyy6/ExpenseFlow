from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):

    category: str = Field(
        min_length=1,
        max_length=100,
    )

    amount: float = Field(
        gt=0,
    )

    month: str = Field(
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
    )


class BudgetUpdate(BaseModel):

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    amount: float | None = Field(
        default=None,
        gt=0,
    )

    month: str | None = Field(
        default=None,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
    )


class BudgetResponse(BaseModel):

    id: int
    user_id: int
    category: str
    amount: float
    month: str

    class Config:
        from_attributes = True