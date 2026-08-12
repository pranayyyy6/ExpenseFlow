from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
)

from app.db.database import Base


class Budget(Base):

    __tablename__ = "budgets"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    category = Column(
        String(100),
        nullable=False,
        index=True,
    )

    amount = Column(
        Float,
        nullable=False,
    )

    month = Column(
        String(7),
        nullable=False,
        index=True,
    )