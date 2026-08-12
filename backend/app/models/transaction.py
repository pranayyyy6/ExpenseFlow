from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from sqlalchemy import ForeignKey

from app.db.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    user_id = Column(
    Integer,
    ForeignKey("users.id"),
    nullable=False,
    index=True,
)

    id = Column(Integer, primary_key=True, index=True)

    transaction_type = Column(
        String(20),
        nullable=False
    )
    # DEBIT / CREDIT

    amount = Column(
        Float,
        nullable=False
    )

    category = Column(
        String(100),
        nullable=True
    )

    description = Column(
        String(500),
        nullable=True
    )

    merchant = Column(
        String(255),
        nullable=True
    )

    transaction_date = Column(
        String(50),
        nullable=True
    )

    payment_method = Column(
        String(50),
        nullable=True
    )
    # UPI / CARD / NET_BANKING / CASH / etc.

    reference_id = Column(
        String(255),
        nullable=True,
        unique=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )