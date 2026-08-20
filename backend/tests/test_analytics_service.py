from unittest import result
from unittest.mock import Mock

import pytest

from app.services.analytics_service import AnalyticsService


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def service(repository):
    return AnalyticsService(repository)


# ============================================================
# BALANCE
# ============================================================

def test_get_balance(service, repository):

    repository.get_total_income.return_value = 10000
    repository.get_total_expense.return_value = 3500

    result = service.get_balance(1)

    assert result == {
        "total_income": 10000.0,
        "total_expense": 3500.0,
        "balance": 6500.0,
    }

    repository.get_total_income.assert_called_once_with(1)
    repository.get_total_expense.assert_called_once_with(1)


def test_get_balance_with_no_data(service, repository):

    repository.get_total_income.return_value = None
    repository.get_total_expense.return_value = None

    result = service.get_balance(1)

    assert result["total_income"] == 0
    assert result["total_expense"] == 0
    assert result["balance"] == 0


# ============================================================
# EXPENSE BY CATEGORY
# ============================================================

def test_get_expense_by_category(service, repository):

    repository.get_expense_by_category.return_value = [
        ("Food", 5000),
        ("Travel", 2500),
        (None, None),
    ]

    result = service.get_expense_by_category(1)

    assert result == [
        {
            "category": "Food",
            "total": 5000.0,
        },
        {
            "category": "Travel",
            "total": 2500.0,
        },
        {
            "category": "Uncategorized",
            "total": 0.0,
        },
    ]


# ============================================================
# EXPENSE BY PAYMENT METHOD
# ============================================================

def test_get_expense_by_payment_method(service, repository):

    repository.get_expense_by_payment_method.return_value = [
        ("UPI", 5000),
        ("CARD", 2500),
        (None, None),
    ]

    result = service.get_expense_by_payment_method(1)

    assert result == [
        {
            "payment_method": "UPI",
            "total": 5000.0,
        },
        {
            "payment_method": "CARD",
            "total": 2500.0,
        },
        {
            "payment_method": "Unknown",
            "total": 0.0,
        },
    ]


# ============================================================
# PROJECTED CASH FLOW
# ============================================================

def test_projected_cash_flow(service, repository):

    repository.get_total_income.return_value = 20000
    repository.get_total_expense.return_value = 8000

    today_bill = Mock()
    today_bill.id = 1
    today_bill.name = "Internet"
    today_bill.amount = 1000
    today_bill.next_due_date = "2026-08-20"
    today_bill.category = "Utilities"

    future_bill = Mock()
    future_bill.id = 2
    future_bill.name = "Rent"
    future_bill.amount = 5000
    future_bill.next_due_date = "2026-08-25"
    future_bill.category = "Housing"

    repository.get_active_recurring_bills.return_value = [
        today_bill,
        future_bill,
    ]

    result = service.get_projected_cash_flow(
        user_id=1,
        days=30,
    )

    assert result["period_days"] == 30
    assert result["total_income"] == 20000
    assert result["actual_expenses"] == 8000
    assert result["current_balance"] == 12000
    assert result["upcoming_bills_total"] == 6000
    assert result["projected_balance"] == 6000

    assert len(result["upcoming_bills"]) == 2


def test_projected_cash_flow_ignores_invalid_and_outside_bills(
    service,
    repository,
):

    repository.get_total_income.return_value = 10000
    repository.get_total_expense.return_value = 2000

    invalid_bill = Mock()
    invalid_bill.next_due_date = "invalid-date"

    old_bill = Mock()
    old_bill.next_due_date = "2020-01-01"

    far_bill = Mock()
    far_bill.next_due_date = "2035-01-01"

    repository.get_active_recurring_bills.return_value = [
        invalid_bill,
        old_bill,
        far_bill,
    ]

    result = service.get_projected_cash_flow(
        user_id=1,
        days=30,
    )

    assert result["upcoming_bills"] == []
    assert result["upcoming_bills_total"] == 0
    assert result["projected_balance"] == 8000


# ============================================================
# MONTHLY ANALYTICS
# ============================================================

def test_get_monthly_analytics_with_top_category(
    service,
    repository,
):

    repository.get_monthly_income.return_value = 10000
    repository.get_monthly_expense.return_value = 4000

    repository.get_top_expense_category.return_value = (
        "Food",
        2500,
    )

    result = service.get_monthly_analytics(
        user_id=1,
        month="2026-08",
    )

    assert result == {
        "month": "2026-08",
        "income": 10000.0,
        "expense": 4000.0,
        "savings": 6000.0,
        "savings_rate": 60.0,
        "top_category": "Food",
        "top_category_amount": 2500.0,
    }


def test_get_monthly_analytics_without_top_category(
    service,
    repository,
):

    repository.get_monthly_income.return_value = None
    repository.get_monthly_expense.return_value = None
    repository.get_top_expense_category.return_value = None

    result = service.get_monthly_analytics(
        user_id=1,
        month="2026-08",
    )

    assert result["income"] == 0
    assert result["expense"] == 0
    assert result["savings"] == 0
    assert result["savings_rate"] == 0
    assert result["top_category"] is None
    assert result["top_category_amount"] == 0


# ============================================================
# SPENDING TRENDS
# ============================================================

def test_get_spending_trends(service, repository):

    repository.get_monthly_totals.return_value = (
        [
            ("2026-07", 10000),
            ("2026-08", 12000),
        ],
        [
            ("2026-07", 6000),
            ("2026-08", 9000),
        ],
    )

    result = service.get_spending_trends(
        user_id=1,
        months=2,
    )

    assert result["months"] == 2
    assert len(result["trend"]) == 2

    july = result["trend"][0]
    august = result["trend"][1]

    assert july["income"] == 10000
    assert july["expense"] == 6000
    assert july["savings"] == 4000
    assert july["expense_change_percent"] is None

    assert august["income"] == 12000
    assert august["expense"] == 9000
    assert august["savings"] == 3000
    assert august["expense_change_percent"] == 50.0


def test_spending_trends_handles_missing_months(
    service,
    repository,
):

    repository.get_monthly_totals.return_value = (
        [],
        [],
    )

    result = service.get_spending_trends(
        user_id=1,
        months=3,
    )

    assert len(result["trend"]) == 3

    for month in result["trend"]:
        assert month["income"] == 0
        assert month["expense"] == 0
        assert month["savings"] == 0
        assert month["expense_change_percent"] is None


def test_spending_trends_rejects_invalid_month_count(
    service,
):

    with pytest.raises(
        ValueError,
        match="months must be between 1 and 24",
    ):
        service.get_spending_trends(
            user_id=1,
            months=0,
        )

    with pytest.raises(
        ValueError,
        match="months must be between 1 and 24",
    ):
        service.get_spending_trends(
            user_id=1,
            months=25,
        )


# ============================================================
# FINANCIAL SUMMARY
# ============================================================

def test_get_financial_summary(
    service,
    repository,
):

    repository.get_total_income.return_value = 20000
    repository.get_total_expense.return_value = 8000

    repository.get_top_expense_category.return_value = (
        "Food",
        3500,
    )

    repository.get_upcoming_bills_total.return_value = 5000

    repository.get_monthly_income.return_value = 20000
    repository.get_monthly_expense.return_value = 8000

    repository.get_top_expense_category.side_effect = [
        ("Food", 3500),
        ("Food", 3500),
    ]

    result = service.get_financial_summary(1)

    assert result["balance"]["total_income"] == 20000
    assert result["balance"]["total_expense"] == 8000
    assert result["balance"]["current_balance"] == 12000

    assert result["monthly"]["income"] == 20000
    assert result["monthly"]["expense"] == 8000
    assert result["monthly"]["savings"] == 12000
    assert result["monthly"]["savings_rate"] == 60.0

    assert result["top_category"]["category"] == "Food"
    assert result["top_category"]["amount"] == 3500

    assert result["upcoming_bills"]["next_30_days_total"] == 5000


def test_financial_summary_with_no_top_category(
    service,
    repository,
):

    repository.get_total_income.return_value = None
    repository.get_total_expense.return_value = None

    repository.get_top_expense_category.return_value = None
    repository.get_upcoming_bills_total.return_value = None

    repository.get_monthly_income.return_value = None
    repository.get_monthly_expense.return_value = None

    result = service.get_financial_summary(1)

    assert result["balance"]["total_income"] == 0
    assert result["balance"]["total_expense"] == 0
    assert result["balance"]["current_balance"] == 0

    assert result["monthly"]["income"] == 0
    assert result["monthly"]["expense"] == 0
    assert result["monthly"]["savings"] == 0
    assert result["monthly"]["savings_rate"] == 0

    assert result["top_category"]["category"] is None
    assert result["top_category"]["amount"] == 0

    assert result["upcoming_bills"]["next_30_days_total"] == 0
# ============================================================
# SPENDING TRENDS - YEAR BOUNDARY
# ============================================================

def test_spending_trends_crosses_previous_year(
    service,
    repository,
    monkeypatch,
):

    from datetime import date

    class FakeDate(date):

        @classmethod
        def today(cls):
            return cls(2026, 1, 15)

    monkeypatch.setattr(
        "app.services.analytics_service.date",
        FakeDate,
    )

    repository.get_monthly_totals.return_value = (
        [],
        [],
    )

    result = service.get_spending_trends(
        user_id=1,
        months=2,
    )

    assert result["months"] == 2

    assert result["trend"][0]["month"] == "2025-12"
    assert result["trend"][1]["month"] == "2026-01"


def test_spending_trends_crosses_next_year(
    service,
    repository,
    monkeypatch,
):

    from datetime import date

    class FakeDate(date):

        @classmethod
        def today(cls):
            return cls(2026, 1, 15)

    monkeypatch.setattr(
        "app.services.analytics_service.date",
        FakeDate,
    )

    repository.get_monthly_totals.return_value = (
        [],
        [],
    )

    result = service.get_spending_trends(
        user_id=1,
        months=13,
    )

    assert result["months"] == 13

    # The implementation generates the 13-month
    # window beginning at January 2025.
    assert result["trend"][0]["month"] == "2025-01"

    # The final month is January 2026.
    assert result["trend"][12]["month"] == "2026-01"