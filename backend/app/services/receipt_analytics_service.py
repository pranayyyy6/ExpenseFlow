from app.repositories.receipt_analytics_repository import (
    ReceiptAnalyticsRepository,
)


class ReceiptAnalyticsService:

    def __init__(
        self,
        repository: ReceiptAnalyticsRepository,
    ):
        self.repository = repository

    # ========================================================
    # RECEIPT SPENDING SUMMARY
    # ========================================================

    def get_receipt_spending(
        self,
        user_id: int,
    ):

        total_receipts = (
            self.repository
            .get_total_receipts(
                user_id
            )
        )

        total_items = (
            self.repository
            .get_total_items(
                user_id
            )
        )

        total_spending = (
            self.repository
            .get_total_spending(
                user_id
            )
        )

        average_receipt = (
            self.repository
            .get_average_receipt_value(
                user_id
            )
        )

        # ----------------------------------------------------
        # Category spending
        # ----------------------------------------------------

        category_rows = (
            self.repository
            .get_spending_by_category(
                user_id
            )
        )

        categories = [
            {
                "category": (
                    category
                    or "Uncategorized"
                ),
                "total": float(
                    total or 0
                ),
            }
            for category, total
            in category_rows
        ]

        # ----------------------------------------------------
        # Top items
        # ----------------------------------------------------

        item_rows = (
            self.repository
            .get_top_items(
                user_id=user_id,
                limit=10,
            )
        )

        top_items = [
            {
                "item_name": (
                    item_name
                    or "Unknown Item"
                ),
                "total_spent": float(
                    total_spent or 0
                ),
                "purchase_count": int(
                    purchase_count or 0
                ),
            }
            for (
                item_name,
                total_spent,
                purchase_count,
            ) in item_rows
        ]

        return {
            "total_receipts": int(
                total_receipts
            ),
            "total_items": int(
                total_items
            ),
            "total_spending": round(
                total_spending,
                2,
            ),
            "average_receipt_value": round(
                average_receipt,
                2,
            ),
            "categories": categories,
            "top_items": top_items,
        }