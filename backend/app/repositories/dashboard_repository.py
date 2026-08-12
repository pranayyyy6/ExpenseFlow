from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.recurring_bill import RecurringBill
from app.models.receipt import Receipt


class DashboardRepository:

    def __init__(self, db: Session):
        self.db = db

    # ========================================================
    # RECENT TRANSACTIONS
    # ========================================================

    def get_recent_transactions(
        self,
        user_id: int,
        limit: int = 5,
    ):
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.user_id == user_id
            )
            .order_by(
                Transaction.id.desc()
            )
            .limit(limit)
            .all()
        )

    # ========================================================
    # UPCOMING BILLS
    # ========================================================

    def get_active_bills(
        self,
        user_id: int,
    ):
        return (
            self.db.query(RecurringBill)
            .filter(
                RecurringBill.user_id == user_id,
                RecurringBill.is_active == True,
            )
            .order_by(
                RecurringBill.next_due_date
            )
            .all()
        )

    # ========================================================
    # RECENT RECEIPTS
    # ========================================================

    def get_recent_receipts(
        self,
        user_id: int,
        limit: int = 5,
    ):
        return (
            self.db.query(Receipt)
            .filter(
                Receipt.user_id == user_id
            )
            .order_by(
                Receipt.id.desc()
            )
            .limit(limit)
            .all()
        )

    # ========================================================
    # TOTAL INCOME
    # ========================================================

    def get_total_income(
        self,
        user_id: int,
    ):
        return (
            self.db.query(
                func.coalesce(
                    func.sum(
                        Transaction.amount
                    ),
                    0,
                )
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "CREDIT",
            )
            .scalar()
        )

    # ========================================================
    # TOTAL EXPENSE
    # ========================================================

    def get_total_expense(
        self,
        user_id: int,
    ):
        return (
            self.db.query(
                func.coalesce(
                    func.sum(
                        Transaction.amount
                    ),
                    0,
                )
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "DEBIT",
            )
            .scalar()
        )