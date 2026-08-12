from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.transaction import Transaction


class BudgetRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    # ========================================================
    # CREATE
    # ========================================================

    def create(
        self,
        budget: Budget,
    ):
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)

        return budget

    # ========================================================
    # GET ALL USER BUDGETS
    # ========================================================

    def get_all(
        self,
        user_id: int,
    ):
        return (
            self.db.query(Budget)
            .filter(
                Budget.user_id == user_id
            )
            .order_by(
                Budget.month.desc(),
                Budget.category,
            )
            .all()
        )

    # ========================================================
    # GET BY ID
    # ========================================================

    def get_by_id(
        self,
        budget_id: int,
        user_id: int,
    ):
        return (
            self.db.query(Budget)
            .filter(
                Budget.id == budget_id,
                Budget.user_id == user_id,
            )
            .first()
        )

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        budget: Budget,
    ):
        self.db.commit()
        self.db.refresh(budget)

        return budget

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        budget: Budget,
    ):
        self.db.delete(budget)
        self.db.commit()

    # ========================================================
    # GET MONTHLY CATEGORY BUDGET
    # ========================================================

    def get_by_category_month(
        self,
        user_id: int,
        category: str,
        month: str,
    ):
        return (
            self.db.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.category == category,
                Budget.month == month,
            )
            .first()
        )

    # ========================================================
    # GET SPENDING FOR BUDGET
    # ========================================================

    def get_spent_for_budget(
        self,
        user_id: int,
        category: str,
        month: str,
    ):
        result = (
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
                Transaction.category == category,
                Transaction.transaction_date.like(
                    f"{month}%"
                ),
            )
            .scalar()
        )

        return float(result or 0)

    # ========================================================
    # GET BUDGET OVERVIEW
    # ========================================================

    def get_budget_overview(
        self,
        user_id: int,
        month: str,
    ):
        return (
            self.db.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.month == month,
            )
            .order_by(
                Budget.category
            )
            .all()
        )