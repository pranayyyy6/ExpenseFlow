from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.recurring_bill import RecurringBill


class AnalyticsRepository:

    def __init__(self, db: Session):
        self.db = db

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
                    func.sum(Transaction.amount),
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
                    func.sum(Transaction.amount),
                    0,
                )
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "DEBIT",
            )
            .scalar()
        )

    # ========================================================
    # ACTIVE RECURRING BILLS
    # ========================================================

    def get_active_recurring_bills(
        self,
        user_id: int,
    ):
        return (
            self.db.query(RecurringBill)
            .filter(
                RecurringBill.user_id == user_id,
                RecurringBill.is_active == True,
            )
            .all()
        )

    # ========================================================
    # EXPENSE BY CATEGORY
    # ========================================================

    def get_expense_by_category(
        self,
        user_id: int,
    ):
        return (
            self.db.query(
                Transaction.category,
                func.sum(
                    Transaction.amount
                ).label("total"),
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "DEBIT",
            )
            .group_by(
                Transaction.category
            )
            .order_by(
                func.sum(
                    Transaction.amount
                ).desc()
            )
            .all()
        )

    # ========================================================
    # EXPENSE BY PAYMENT METHOD
    # ========================================================

    def get_expense_by_payment_method(
        self,
        user_id: int,
    ):
        return (
            self.db.query(
                Transaction.payment_method,
                func.sum(
                    Transaction.amount
                ).label("total"),
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "DEBIT",
            )
            .group_by(
                Transaction.payment_method
            )
            .order_by(
                func.sum(
                    Transaction.amount
                ).desc()
            )
            .all()
        )

    # ========================================================
    # MONTHLY INCOME
    # ========================================================

    def get_monthly_income(
        self,
        user_id: int,
        month: str,
    ):
        return (
            self.db.query(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                )
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "CREDIT",
                Transaction.transaction_date.like(
                    f"{month}%"
                ),
            )
            .scalar()
        )

    # ========================================================
    # MONTHLY EXPENSE
    # ========================================================

    def get_monthly_expense(
        self,
        user_id: int,
        month: str,
    ):
        return (
            self.db.query(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                )
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "DEBIT",
                Transaction.transaction_date.like(
                    f"{month}%"
                ),
            )
            .scalar()
        )

    # ========================================================
    # TOP EXPENSE CATEGORY
    # ========================================================

    def get_top_expense_category(
        self,
        user_id: int,
        month: str,
    ):
        return (
            self.db.query(
                Transaction.category,
                func.sum(
                    Transaction.amount
                ).label("total"),
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "DEBIT",
                Transaction.transaction_date.like(
                    f"{month}%"
                ),
            )
            .group_by(
                Transaction.category
            )
            .order_by(
                func.sum(
                    Transaction.amount
                ).desc()
            )
            .first()
        )

    # ========================================================
    # MONTHLY TOTALS
    #
    # Used by:
    # GET /analytics/trends
    #
    # Returns:
    #     income grouped by YYYY-MM
    #     expense grouped by YYYY-MM
    # ========================================================

    def get_monthly_totals(
        self,
        user_id: int,
        start_date: str,
    ):

        # SQLite:
        #
        # transaction_date:
        # 2026-08-05
        #
        # substr(..., 1, 7):
        # 2026-08

        month_expr = func.substr(
            Transaction.transaction_date,
            1,
            7,
        )

        # ----------------------------------------------------
        # MONTHLY INCOME
        # ----------------------------------------------------

        income = (
            self.db.query(
                month_expr.label("month"),
                func.sum(
                    Transaction.amount
                ).label("total"),
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "CREDIT",
                Transaction.transaction_date >= start_date,
            )
            .group_by(
                month_expr
            )
            .all()
        )

        # ----------------------------------------------------
        # MONTHLY EXPENSE
        # ----------------------------------------------------

        expense = (
            self.db.query(
                month_expr.label("month"),
                func.sum(
                    Transaction.amount
                ).label("total"),
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "DEBIT",
                Transaction.transaction_date >= start_date,
            )
            .group_by(
                month_expr
            )
            .all()
        )

        return income, expense
    # ========================================================
    # UPCOMING BILLS TOTAL
    # ========================================================

    def get_upcoming_bills_total(
        self,
        user_id: int,
        end_date: str,
    ):
        return (
            self.db.query(
                func.coalesce(
                    func.sum(
                        RecurringBill.amount
                    ),
                    0,
                )
            )
            .filter(
                RecurringBill.user_id == user_id,
                RecurringBill.is_active == True,
                RecurringBill.next_due_date <= end_date,
            )
            .scalar()
        )