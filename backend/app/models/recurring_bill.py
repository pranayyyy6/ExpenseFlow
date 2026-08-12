from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Float,
)

from app.db.database import Base


class RecurringBill(Base):

    __tablename__ = "recurring_bills"

    user_id = Column(
    Integer,
    ForeignKey("users.id"),
    nullable=True,
    index=True,
)

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    amount = Column(
        Float,
        nullable=False,
    )

    frequency = Column(
        String(50),
        nullable=False,
    )

    next_due_date = Column(
        String(50),
        nullable=False,
    )

    category = Column(
        String(100),
        nullable=False,
        default="Bills",
    )

    payment_method = Column(
        String(50),
        nullable=True,
    )

    auto_pay = Column(
        Boolean,
        default=False,
    )

    is_active = Column(
        Boolean,
        default=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )