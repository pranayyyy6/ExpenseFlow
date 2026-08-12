from datetime import date, datetime, timedelta

from app.repositories.analytics_repository import (
    AnalyticsRepository,
)


class AnalyticsService:

    def __init__(
        self,
        repository: AnalyticsRepository,
    ):
        self.repository = repository

    # ========================================================
    # BALANCE
    # ========================================================

    def get_balance(
        self,
        user_id: int,
    ):

        income = (
            self.repository
            .get_total_income(user_id)
        )

        expense = (
            self.repository
            .get_total_expense(user_id)
        )

        return {
            "total_income": float(income or 0),
            "total_expense": float(expense or 0),
            "balance": float(
                (income or 0) - (expense or 0)
            ),
        }

    # ========================================================
    # EXPENSE BY CATEGORY
    # ========================================================

    def get_expense_by_category(
        self,
        user_id: int,
    ):

        results = (
            self.repository
            .get_expense_by_category(user_id)
        )

        return [
            {
                "category": (
                    category
                    or "Uncategorized"
                ),
                "total": float(total or 0),
            }
            for category, total in results
        ]

    # ========================================================
    # EXPENSE BY PAYMENT METHOD
    # ========================================================

    def get_expense_by_payment_method(
        self,
        user_id: int,
    ):

        results = (
            self.repository
            .get_expense_by_payment_method(
                user_id
            )
        )

        return [
            {
                "payment_method": (
                    method
                    or "Unknown"
                ),
                "total": float(total or 0),
            }
            for method, total in results
        ]

    # ========================================================
    # PROJECTED CASH FLOW
    # ========================================================

    def get_projected_cash_flow(
        self,
        user_id: int,
        days: int = 30,
    ):

        income = (
            self.repository
            .get_total_income(user_id)
            or 0
        )

        expense = (
            self.repository
            .get_total_expense(user_id)
            or 0
        )

        current_balance = (
            income - expense
        )

        today = date.today()

        end_date = (
            today + timedelta(days=days)
        )

        bills = (
            self.repository
            .get_active_recurring_bills(
                user_id
            )
        )

        upcoming_bills = []

        for bill in bills:

            try:
                due_date = datetime.strptime(
                    bill.next_due_date,
                    "%Y-%m-%d",
                ).date()

            except ValueError:
                continue

            if today <= due_date <= end_date:

                days_remaining = (
                    due_date - today
                ).days

                upcoming_bills.append(
                    {
                        "id": bill.id,
                        "name": bill.name,
                        "amount": bill.amount,
                        "due_date": (
                            bill.next_due_date
                        ),
                        "days_remaining": (
                            days_remaining
                        ),
                        "category": bill.category,
                    }
                )

        upcoming_bills.sort(
            key=lambda bill:
            bill["days_remaining"]
        )

        upcoming_total = sum(
            bill["amount"]
            for bill in upcoming_bills
        )

        projected_balance = (
            current_balance
            - upcoming_total
        )

        return {
            "period_days": days,
            "total_income": float(income),
            "actual_expenses": float(expense),
            "current_balance": float(
                current_balance
            ),
            "upcoming_bills_total": float(
                upcoming_total
            ),
            "projected_balance": float(
                projected_balance
            ),
            "upcoming_bills": upcoming_bills,
        }

    # ========================================================
    # MONTHLY ANALYTICS
    # ========================================================

    def get_monthly_analytics(
        self,
        user_id: int,
        month: str,
    ):

        income = float(
            self.repository
            .get_monthly_income(
                user_id=user_id,
                month=month,
            )
            or 0
        )

        expense = float(
            self.repository
            .get_monthly_expense(
                user_id=user_id,
                month=month,
            )
            or 0
        )

        savings = (
            income - expense
        )

        savings_rate = (
            (savings / income) * 100
            if income > 0
            else 0
        )

        top_category = (
            self.repository
            .get_top_expense_category(
                user_id=user_id,
                month=month,
            )
        )

        if top_category:

            category_name = (
                top_category[0]
                or "Uncategorized"
            )

            category_amount = float(
                top_category[1] or 0
            )

        else:

            category_name = None
            category_amount = 0

        return {
            "month": month,
            "income": income,
            "expense": expense,
            "savings": savings,
            "savings_rate": round(
                savings_rate,
                2,
            ),
            "top_category": category_name,
            "top_category_amount": (
                category_amount
            ),
        }
     # ========================================================
    # SPENDING TRENDS
    # ========================================================

    def get_spending_trends(
        self,
        user_id: int,
        months: int = 6,
    ):

        if months < 1 or months > 24:
            raise ValueError(
                "months must be between 1 and 24"
            )

        today = date.today()

        # First day of current month
        start_month = today.replace(day=1)

        # Move backwards months - 1 times
        for _ in range(months - 1):

            if start_month.month == 1:

                start_month = start_month.replace(
                    year=start_month.year - 1,
                    month=12,
                )

            else:

                start_month = start_month.replace(
                    month=start_month.month - 1
                )

        start_date = start_month.strftime(
            "%Y-%m-%d"
        )

        # ----------------------------------------------------
        # Get monthly totals from repository
        # ----------------------------------------------------

        income_rows, expense_rows = (
            self.repository.get_monthly_totals(
                user_id=user_id,
                start_date=start_date,
            )
        )

        # ----------------------------------------------------
        # Convert query results into dictionaries
        # ----------------------------------------------------

        income_map = {
            month: float(total or 0)
            for month, total in income_rows
        }

        expense_map = {
            month: float(total or 0)
            for month, total in expense_rows
        }

        # ----------------------------------------------------
        # Build all requested months
        # ----------------------------------------------------

        results = []

        current = start_month

        for _ in range(months):

            month = current.strftime(
                "%Y-%m"
            )

            income = income_map.get(
                month,
                0,
            )

            expense = expense_map.get(
                month,
                0,
            )

            savings = (
                income - expense
            )

            results.append(
                {
                    "month": month,
                    "income": income,
                    "expense": expense,
                    "savings": savings,
                }
            )

            # Move to next month
            if current.month == 12:

                current = current.replace(
                    year=current.year + 1,
                    month=1,
                )

            else:

                current = current.replace(
                    month=current.month + 1
                )

        # ----------------------------------------------------
        # Calculate month-over-month expense change
        # ----------------------------------------------------

        for index, result in enumerate(results):

            if index == 0:

                result[
                    "expense_change_percent"
                ] = None

                continue

            previous_expense = results[
                index - 1
            ]["expense"]

            current_expense = result[
                "expense"
            ]

            if previous_expense == 0:

                result[
                    "expense_change_percent"
                ] = None

            else:

                change = (
                    (
                        current_expense
                        - previous_expense
                    )
                    / previous_expense
                ) * 100

                result[
                    "expense_change_percent"
                ] = round(
                    change,
                    2,
                )

        return {
            "months": months,
            "trend": results,
        }   
    # ========================================================
    # FINANCIAL SUMMARY
    # ========================================================

    def get_financial_summary(
        self,
        user_id: int,
    ):

        # ----------------------------------------------------
        # Overall balance
        # ----------------------------------------------------

        income = float(
            self.repository
            .get_total_income(user_id)
            or 0
        )

        expense = float(
            self.repository
            .get_total_expense(user_id)
            or 0
        )

        savings = income - expense

        savings_rate = (
            (savings / income) * 100
            if income > 0
            else 0
        )

        # ----------------------------------------------------
        # Current month
        # ----------------------------------------------------

        current_month = date.today().strftime(
            "%Y-%m"
        )

        # ----------------------------------------------------
        # Top category this month
        # ----------------------------------------------------

        top_category = (
            self.repository
            .get_top_expense_category(
                user_id=user_id,
                month=current_month,
            )
        )

        if top_category:

            top_category_name = (
                top_category[0]
                or "Uncategorized"
            )

            top_category_amount = float(
                top_category[1] or 0
            )

        else:

            top_category_name = None
            top_category_amount = 0

        # ----------------------------------------------------
        # Upcoming bills - next 30 days
        # ----------------------------------------------------

        today = date.today()

        end_date = (
            today + timedelta(days=30)
        ).strftime("%Y-%m-%d")

        upcoming_bills_total = float(
            self.repository
            .get_upcoming_bills_total(
                user_id=user_id,
                end_date=end_date,
            )
            or 0
        )

        # ----------------------------------------------------
        # Monthly analytics
        # ----------------------------------------------------

        monthly = (
            self.get_monthly_analytics(
                user_id=user_id,
                month=current_month,
            )
        )

        # ----------------------------------------------------
        # Final response
        # ----------------------------------------------------

        return {
            "month": current_month,

            "balance": {
                "total_income": income,
                "total_expense": expense,
                "current_balance": savings,
            },

            "monthly": {
                "income": monthly["income"],
                "expense": monthly["expense"],
                "savings": monthly["savings"],
                "savings_rate": monthly[
                    "savings_rate"
                ],
            },

            "top_category": {
                "category": top_category_name,
                "amount": top_category_amount,
            },

            "upcoming_bills": {
                "next_30_days_total": (
                    upcoming_bills_total
                ),
            },
        }