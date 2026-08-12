from datetime import date, datetime

from app.repositories.dashboard_repository import (
    DashboardRepository,
)

from app.repositories.analytics_repository import (
    AnalyticsRepository,
)

from app.repositories.budget_repository import (
    BudgetRepository,
)

from app.repositories.receipt_analytics_repository import (
    ReceiptAnalyticsRepository,
)


class DashboardService:

    def __init__(
        self,
        repository: DashboardRepository,
        analytics_repository: AnalyticsRepository,
        budget_repository: BudgetRepository,
        receipt_analytics_repository: ReceiptAnalyticsRepository,
    ):
        self.repository = repository
        self.analytics_repository = (
            analytics_repository
        )
        self.budget_repository = (
            budget_repository
        )
        self.receipt_analytics_repository = (
            receipt_analytics_repository
        )

    # ========================================================
    # DASHBOARD
    # ========================================================

    def get_dashboard(
        self,
        user_id: int,
    ):

        # ====================================================
        # FINANCIAL BALANCE
        # ====================================================

        income = float(
            self.repository
            .get_total_income(
                user_id
            )
            or 0
        )

        expense = float(
            self.repository
            .get_total_expense(
                user_id
            )
            or 0
        )

        balance = income - expense

        savings_rate = (
            (balance / income) * 100
            if income > 0
            else 0
        )

        # ====================================================
        # RECENT TRANSACTIONS
        # ====================================================

        transactions = (
            self.repository
            .get_recent_transactions(
                user_id=user_id,
                limit=5,
            )
        )

        recent_transactions = []

        for transaction in transactions:

            recent_transactions.append(
                {
                    "id": transaction.id,
                    "type": (
                        transaction.transaction_type
                    ),
                    "amount": float(
                        transaction.amount
                    ),
                    "category": (
                        transaction.category
                    ),
                    "merchant": (
                        transaction.merchant
                    ),
                    "date": (
                        transaction.transaction_date
                    ),
                    "payment_method": (
                        transaction.payment_method
                    ),
                }
            )

        # ====================================================
        # UPCOMING BILLS
        # ====================================================

        bills = (
            self.repository
            .get_active_bills(
                user_id
            )
        )

        today = date.today()

        upcoming_bills = []

        for bill in bills:

            try:

                due_date = datetime.strptime(
                    bill.next_due_date,
                    "%Y-%m-%d",
                ).date()

            except (ValueError, TypeError):

                continue

            if due_date < today:
                continue

            days_remaining = (
                due_date - today
            ).days

            upcoming_bills.append(
                {
                    "id": bill.id,
                    "name": bill.name,
                    "amount": float(
                        bill.amount
                    ),
                    "due_date": (
                        bill.next_due_date
                    ),
                    "days_remaining": (
                        days_remaining
                    ),
                    "category": (
                        bill.category
                    ),
                    "auto_pay": (
                        bill.auto_pay
                    ),
                }
            )

        upcoming_bills.sort(
            key=lambda bill:
            bill["days_remaining"]
        )

        upcoming_bills_total = sum(
            bill["amount"]
            for bill in upcoming_bills
        )

        # ====================================================
        # RECENT RECEIPTS
        # ====================================================

        receipts = (
            self.repository
            .get_recent_receipts(
                user_id=user_id,
                limit=5,
            )
        )

        recent_receipts = []

        for receipt in receipts:

            recent_receipts.append(
                {
                    "id": receipt.id,
                    "store_name": (
                        receipt.store_name
                    ),
                    "receipt_date": (
                        receipt.receipt_date
                    ),
                    "total_amount": (
                        float(
                            receipt.total_amount
                        )
                        if receipt.total_amount
                        is not None
                        else None
                    ),
                    "image_path": (
                        receipt.image_path
                    ),
                }
            )

        # ====================================================
        # BUDGET OVERVIEW
        # ====================================================

        current_month = (
            today.strftime("%Y-%m")
        )

        budgets = (
            self.budget_repository
            .get_budget_overview(
                user_id=user_id,
                month=current_month,
            )
        )

        budget_items = []

        total_budget = 0.0
        total_budget_spent = 0.0

        budget_on_track = 0
        budget_warning = 0
        budget_exceeded = 0

        for budget in budgets:

            spent = (
                self.budget_repository
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
                (spent / budget_amount)
                * 100
                if budget_amount > 0
                else 0
            )

            if spent > budget_amount:

                budget_status = "EXCEEDED"
                budget_exceeded += 1

            elif utilization >= 80:

                budget_status = "WARNING"
                budget_warning += 1

            else:

                budget_status = "ON_TRACK"
                budget_on_track += 1

            budget_items.append(
                {
                    "id": budget.id,
                    "category": (
                        budget.category
                    ),
                    "budget": budget_amount,
                    "spent": spent,
                    "remaining": remaining,
                    "utilization_percent": round(
                        utilization,
                        2,
                    ),
                    "status": budget_status,
                }
            )

            total_budget += budget_amount
            total_budget_spent += spent

        # ====================================================
        # TOP SPENDING CATEGORIES
        # ====================================================

        category_rows = (
            self.analytics_repository
            .get_expense_by_category(
                user_id
            )
        )

        top_categories = [
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
            in category_rows[:5]
        ]

        # ====================================================
        # RECEIPT ANALYTICS
        # ====================================================

        total_receipts = (
            self.receipt_analytics_repository
            .get_total_receipts(
                user_id
            )
        )

        receipt_spending = (
            self.receipt_analytics_repository
            .get_total_spending(
                user_id
            )
        )

        average_receipt = (
            self.receipt_analytics_repository
            .get_average_receipt_value(
                user_id
            )
        )

        # ====================================================
        # SPENDING TRENDS
        # ====================================================

        # Last 6 months

        month_rows = (
            self.analytics_repository
            .get_monthly_totals(
                user_id=user_id,
                start_date=(
                    today.replace(
                        day=1
                    ).strftime(
                        "%Y-%m-%d"
                    )
                ),
            )
        )

        income_rows, expense_rows = (
            month_rows
        )

        income_map = {
            month: float(total or 0)
            for month, total
            in income_rows
        }

        expense_map = {
            month: float(total or 0)
            for month, total
            in expense_rows
        }

        spending_trends = []

        current_month_date = today.replace(
            day=1
        )

        for _ in range(6):

            month = (
                current_month_date
                .strftime("%Y-%m")
            )

            month_income = (
                income_map.get(
                    month,
                    0,
                )
            )

            month_expense = (
                expense_map.get(
                    month,
                    0,
                )
            )

            spending_trends.append(
                {
                    "month": month,
                    "income": month_income,
                    "expense": month_expense,
                    "savings": (
                        month_income
                        - month_expense
                    ),
                }
            )

            if (
                current_month_date.month
                == 1
            ):

                current_month_date = (
                    current_month_date
                    .replace(
                        year=(
                            current_month_date.year
                            - 1
                        ),
                        month=12,
                    )
                )

            else:

                current_month_date = (
                    current_month_date
                    .replace(
                        month=(
                            current_month_date.month
                            - 1
                        )
                    )
                )

        spending_trends.reverse()

        # ====================================================
        # FINAL DASHBOARD
        # ====================================================

        return {

            "financial": {

                "total_income": income,

                "total_expense": expense,

                "current_balance": balance,

                "savings_rate": round(
                    savings_rate,
                    2,
                ),
            },

            "budgets": {

                "total_budget": (
                    total_budget
                ),

                "total_spent": (
                    total_budget_spent
                ),

                "total_remaining": (
                    total_budget
                    - total_budget_spent
                ),

                "on_track": (
                    budget_on_track
                ),

                "warning": (
                    budget_warning
                ),

                "exceeded": (
                    budget_exceeded
                ),

                "items": budget_items,
            },

            "receipts": {

                "total_receipts": int(
                    total_receipts
                ),

                "total_spending": round(
                    float(
                        receipt_spending
                        or 0
                    ),
                    2,
                ),

                "average_receipt": round(
                    float(
                        average_receipt
                        or 0
                    ),
                    2,
                ),
            },

            "upcoming_bills": {

                "total": round(
                    upcoming_bills_total,
                    2,
                ),

                "count": len(
                    upcoming_bills
                ),

                "items": upcoming_bills,
            },

            "top_categories": (
                top_categories
            ),

            "spending_trends": (
                spending_trends
            ),

            "recent_transactions": (
                recent_transactions
            ),

            "recent_receipts": (
                recent_receipts
            ),
        }