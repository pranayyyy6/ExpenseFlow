from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import relationship

from app.db.database import Base


class ReceiptItem(Base):

    __tablename__ = "receipt_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    receipt_id = Column(
        Integer,
        ForeignKey("receipts.id"),
    )

    item_name = Column(
        String(255),
        nullable=False,
    )

    quantity = Column(
        Integer,
        default=1,
    )

    price = Column(
        Float,
        nullable=False,
    )

    category = Column(
        String(100),
        default="Uncategorized",
    )

    receipt = relationship(
        "Receipt",
        back_populates="items",
    )