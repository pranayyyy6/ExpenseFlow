from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import relationship

from app.db.database import Base


class Receipt(Base):

    __tablename__ = "receipts"

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

    store_name = Column(
        String(255),
        nullable=False,
    )

    receipt_date = Column(
        String(50),
        nullable=True,
    )

    total_amount = Column(
        Float,
        nullable=True,
    )

    image_path = Column(
        String(500),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    items = relationship(
        "ReceiptItem",
        back_populates="receipt",
        cascade="all, delete-orphan",
    )