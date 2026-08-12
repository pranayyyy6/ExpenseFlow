from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.repositories.budget_repository import BudgetRepository


class BudgetService:

    def __init__(
        self,
        repository: BudgetRepository,
    ):
        self.repository = repository

    # ========================================================
    # CREATE
    # ========================================================

    def create_budget(
        self,
        user_id: int,
        category: str,
        amount: float,
        month: str,
    ):
        # Prevent duplicate budget for the same
        # user + category + month.

        existing = (
            self.repository
            .get_by_category_month(
                user_id=user_id,
                category=category,
                month=month,
            )
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Budget already exists for "
                    f"{category} in {month}"
                ),
            )

        budget = Budget(
            user_id=user_id,
            category=category,
            amount=amount,
            month=month,
        )

        return self.repository.create(
            budget
        )

    # ========================================================
    # GET ALL
    # ========================================================

    def get_budgets(
        self,
        user_id: int,
    ):
        return self.repository.get_all(
            user_id
        )

    # ========================================================
    # GET BY ID
    # ========================================================

    def get_budget(
        self,
        budget_id: int,
        user_id: int,
    ):
        budget = (
            self.repository
            .get_by_id(
                budget_id=budget_id,
                user_id=user_id,
            )
        )

        if budget is None:
            raise HTTPException(
                status_code=404,
                detail="Budget not found",
            )

        return budget

    # ========================================================
    # UPDATE
    # ========================================================

    def update_budget(
        self,
        budget_id: int,
        user_id: int,
        update_data: dict,
    ):
        budget = self.get_budget(
            budget_id=budget_id,
            user_id=user_id,
        )

        new_category = update_data.get(
            "category",
            budget.category,
        )

        new_month = update_data.get(
            "month",
            budget.month,
        )

        # Check duplicate after update.

        existing = (
            self.repository
            .get_by_category_month(
                user_id=user_id,
                category=new_category,
                month=new_month,
            )
        )

        if (
            existing
            and existing.id != budget.id
        ):
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Budget already exists for "
                    f"{new_category} in {new_month}"
                ),
            )

        for key, value in update_data.items():
            setattr(
                budget,
                key,
                value,
            )

        return self.repository.update(
            budget
        )

    # ========================================================
    # DELETE
    # ========================================================

    def delete_budget(
        self,
        budget_id: int,
        user_id: int,
    ):
        budget = self.get_budget(
            budget_id=budget_id,
            user_id=user_id,
        )

        self.repository.delete(
            budget
        )

        return {
            "message": "Budget deleted successfully",
            "budget_id": budget_id,
        }
    # ========================================================
    # BUDGET STATUS
    # ========================================================

    def get_budget_status(
        self,
        budget_id: int,
        user_id: int,
    ):

        budget = self.get_budget(
            budget_id=budget_id,
            user_id=user_id,
        )

        spent = (
            self.repository
            .get_spent_for_budget(
                user_id=user_id,
                category=budget.category,
                month=budget.month,
            )
        )

        remaining = (
            budget.amount - spent
        )

        utilization = (
            (spent / budget.amount) * 100
            if budget.amount > 0
            else 0
        )

        if spent > budget.amount:
            status = "EXCEEDED"

        elif utilization >= 80:
            status = "WARNING"

        else:
            status = "ON_TRACK"

        return {
            "budget_id": budget.id,
            "category": budget.category,
            "month": budget.month,
            "budget": budget.amount,
            "spent": spent,
            "remaining": remaining,
            "utilization_percent": round(
                utilization,
                2,
            ),
            "status": status,
        }
    # ========================================================
    # BUDGET OVERVIEW
    # ========================================================

    def get_budget_overview(
        self,
        user_id: int,
        month: str,
    ):

        budgets = (
            self.repository
            .get_budget_overview(
                user_id=user_id,
                month=month,
            )
        )

        overview = []

        total_budget = 0.0
        total_spent = 0.0

        on_track = 0
        warning = 0
        exceeded = 0

        for budget in budgets:

            spent = (
                self.repository
                .get_spent_for_budget(
                    user_id=user_id,
                    category=budget.category,
                    month=budget.month,
                )
            )

            budget_amount = float(
                budget.amount
            )

            spent = float(spent)

            remaining = (
                budget_amount - spent
            )

            utilization = (
                (spent / budget_amount) * 100
                if budget_amount > 0
                else 0
            )

            if spent > budget_amount:
                status = "EXCEEDED"
                exceeded += 1

            elif utilization >= 80:
                status = "WARNING"
                warning += 1

            else:
                status = "ON_TRACK"
                on_track += 1

            overview.append(
                {
                    "id": budget.id,
                    "category": budget.category,
                    "month": budget.month,
                    "budget": budget_amount,
                    "spent": spent,
                    "remaining": remaining,
                    "utilization_percent": round(
                        utilization,
                        2,
                    ),
                    "status": status,
                }
            )

            total_budget += budget_amount
            total_spent += spent

        total_remaining = (
            total_budget - total_spent
        )

        return {
            "month": month,
            "budgets": overview,
            "summary": {
                "total_budget": total_budget,
                "total_spent": total_spent,
                "total_remaining": total_remaining,
                "on_track": on_track,
                "warning": warning,
                "exceeded": exceeded,
            },
        }