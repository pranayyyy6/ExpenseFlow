from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.receipt import Receipt
from app.models.receipt_item import ReceiptItem


class ReceiptAnalyticsRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    # ========================================================
    # TOTAL RECEIPTS
    # ========================================================

    def get_total_receipts(
        self,
        user_id: int,
    ):
        return (
            self.db.query(
                func.count(Receipt.id)
            )
            .filter(
                Receipt.user_id == user_id
            )
            .scalar()
        ) or 0

    # ========================================================
    # TOTAL ITEMS
    # ========================================================

    def get_total_items(
        self,
        user_id: int,
    ):
        return (
            self.db.query(
                func.coalesce(
                    func.sum(
                        ReceiptItem.quantity
                    ),
                    0,
                )
            )
            .join(
                Receipt,
                ReceiptItem.receipt_id
                == Receipt.id,
            )
            .filter(
                Receipt.user_id == user_id
            )
            .scalar()
        ) or 0

    # ========================================================
    # TOTAL RECEIPT SPENDING
    # ========================================================

    def get_total_spending(
        self,
        user_id: int,
    ):
        result = (
            self.db.query(
                func.coalesce(
                    func.sum(
                        ReceiptItem.quantity
                        * ReceiptItem.price
                    ),
                    0,
                )
            )
            .join(
                Receipt,
                ReceiptItem.receipt_id
                == Receipt.id,
            )
            .filter(
                Receipt.user_id == user_id
            )
            .scalar()
        )

        return float(result or 0)

    # ========================================================
    # SPENDING BY CATEGORY
    # ========================================================

    def get_spending_by_category(
        self,
        user_id: int,
    ):
        return (
            self.db.query(
                ReceiptItem.category,
                func.sum(
                    ReceiptItem.quantity
                    * ReceiptItem.price
                ).label("total"),
            )
            .join(
                Receipt,
                ReceiptItem.receipt_id
                == Receipt.id,
            )
            .filter(
                Receipt.user_id == user_id
            )
            .group_by(
                ReceiptItem.category
            )
            .order_by(
                func.sum(
                    ReceiptItem.quantity
                    * ReceiptItem.price
                ).desc()
            )
            .all()
        )

    # ========================================================
    # TOP ITEMS
    # ========================================================

    def get_top_items(
        self,
        user_id: int,
        limit: int = 10,
    ):
        return (
            self.db.query(
                ReceiptItem.item_name,
                func.sum(
                    ReceiptItem.quantity
                    * ReceiptItem.price
                ).label("total_spent"),
                func.sum(
                    ReceiptItem.quantity
                ).label("purchase_count"),
            )
            .join(
                Receipt,
                ReceiptItem.receipt_id
                == Receipt.id,
            )
            .filter(
                Receipt.user_id == user_id
            )
            .group_by(
                ReceiptItem.item_name
            )
            .order_by(
                func.sum(
                    ReceiptItem.quantity
                    * ReceiptItem.price
                ).desc()
            )
            .limit(limit)
            .all()
        )

    # ========================================================
    # AVERAGE RECEIPT VALUE
    # ========================================================

    def get_average_receipt_value(
        self,
        user_id: int,
    ):
        result = (
            self.db.query(
                func.coalesce(
                    func.avg(
                        Receipt.total_amount
                    ),
                    0,
                )
            )
            .filter(
                Receipt.user_id == user_id
            )
            .scalar()
        )

        return float(result or 0)