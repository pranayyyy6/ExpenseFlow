def register_user(client, email):

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": "Analytics User",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_transaction(
    client,
    token,
    transaction_type,
    amount,
    category,
):

    return client.post(
        "/transactions/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "transaction_type": transaction_type,
            "amount": amount,
            "category": category,
            "description": "Test transaction",
            "merchant": "Test Merchant",
            "transaction_date": "2026-08-12",
            "payment_method": "UPI",
            "reference_id": None,
        },
    )


def test_balance_analytics(client):

    token = register_user(
        client,
        "analytics-balance@example.com",
    )

    create_transaction(
        client,
        token,
        "CREDIT",
        10000,
        "Salary",
    )

    create_transaction(
        client,
        token,
        "DEBIT",
        3000,
        "Food",
    )

    response = client.get(
        "/analytics/balance",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_income"] == 10000
    assert data["total_expense"] == 3000
    assert data["balance"] == 7000


def test_category_analytics(client):

    token = register_user(
        client,
        "analytics-category@example.com",
    )

    create_transaction(
        client,
        token,
        "DEBIT",
        3000,
        "Food",
    )

    create_transaction(
        client,
        token,
        "DEBIT",
        2000,
        "Shopping",
    )

    create_transaction(
        client,
        token,
        "DEBIT",
        1000,
        "Food",
    )

    response = client.get(
        "/analytics/by-category",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data[0]["category"] == "Food"
    assert data[0]["total"] == 4000

    assert data[1]["category"] == "Shopping"
    assert data[1]["total"] == 2000

# ============================================================
# ANALYTICS REPOSITORY COVERAGE
# ============================================================

def test_analytics_repository_methods(
    db_session,
):
    from app.repositories.analytics_repository import (
        AnalyticsRepository,
    )

    from app.models.transaction import Transaction
    from app.models.recurring_bill import RecurringBill

    repository = AnalyticsRepository(
        db_session
    )

    # --------------------------------------------------------
    # Transactions
    # --------------------------------------------------------

    credit = Transaction(
        user_id=999,
        transaction_type="CREDIT",
        amount=10000,
        category="Salary",
        description="Salary",
        merchant="Company",
        transaction_date="2026-08-10",
        payment_method="BANK",
        reference_id=None,
    )

    debit_food = Transaction(
        user_id=999,
        transaction_type="DEBIT",
        amount=3000,
        category="Food",
        description="Lunch",
        merchant="Restaurant",
        transaction_date="2026-08-12",
        payment_method="UPI",
        reference_id=None,
    )

    debit_shopping = Transaction(
        user_id=999,
        transaction_type="DEBIT",
        amount=2000,
        category="Shopping",
        description="Clothes",
        merchant="Store",
        transaction_date="2026-08-15",
        payment_method="CARD",
        reference_id=None,
    )

    db_session.add_all(
        [
            credit,
            debit_food,
            debit_shopping,
        ]
    )

    # --------------------------------------------------------
    # Recurring bill
    # --------------------------------------------------------

    bill = RecurringBill(
        user_id=999,
        name="Netflix",
        amount=649,
        frequency="MONTHLY",
        next_due_date="2026-08-20",
        category="Entertainment",
        payment_method="CARD",
        auto_pay=True,
        is_active=True,
    )

    db_session.add(bill)

    db_session.commit()

    # --------------------------------------------------------
    # Expense by payment method
    # --------------------------------------------------------

    payment_methods = (
        repository.get_expense_by_payment_method(
            user_id=999
        )
    )

    assert len(payment_methods) == 2

    # Highest expense first
    assert payment_methods[0][1] == 3000
    assert payment_methods[1][1] == 2000

    # --------------------------------------------------------
    # Monthly income
    # --------------------------------------------------------

    monthly_income = (
        repository.get_monthly_income(
            user_id=999,
            month="2026-08",
        )
    )

    assert monthly_income == 10000

    # --------------------------------------------------------
    # Monthly expense
    # --------------------------------------------------------

    monthly_expense = (
        repository.get_monthly_expense(
            user_id=999,
            month="2026-08",
        )
    )

    assert monthly_expense == 5000

    # --------------------------------------------------------
    # Top expense category
    # --------------------------------------------------------

    top_category = (
        repository.get_top_expense_category(
            user_id=999,
            month="2026-08",
        )
    )

    assert top_category is not None
    assert top_category[0] == "Food"
    assert top_category[1] == 3000

    # --------------------------------------------------------
    # Monthly totals
    # --------------------------------------------------------

    income_rows, expense_rows = (
        repository.get_monthly_totals(
            user_id=999,
            start_date="2026-08-01",
        )
    )

    income_map = {
        month: total
        for month, total
        in income_rows
    }

    expense_map = {
        month: total
        for month, total
        in expense_rows
    }

    assert income_map["2026-08"] == 10000
    assert expense_map["2026-08"] == 5000

    # --------------------------------------------------------
    # Active recurring bills
    # --------------------------------------------------------

    active_bills = (
        repository.get_active_recurring_bills(
            user_id=999
        )
    )

    assert len(active_bills) == 1
    assert active_bills[0].name == "Netflix"

    # --------------------------------------------------------
    # Upcoming bills total
    # --------------------------------------------------------

    upcoming_total = (
        repository.get_upcoming_bills_total(
            user_id=999,
            end_date="2026-08-31",
        )
    )

    assert upcoming_total == 649

# ============================================================
# PAYMENT METHOD ANALYTICS
# ============================================================

def test_payment_method_analytics(client):

    token = register_user(
        client,
        "analytics-payment@example.com",
    )

    create_transaction(
        client,
        token,
        "DEBIT",
        3000,
        "Food",
    )

    create_transaction(
        client,
        token,
        "DEBIT",
        2000,
        "Shopping",
    )

    response = client.get(
        "/analytics/by-payment-method",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# PROJECTED CASH FLOW
# ============================================================

def test_projected_cash_flow(client):

    token = register_user(
        client,
        "analytics-cashflow@example.com",
    )

    create_transaction(
        client,
        token,
        "CREDIT",
        10000,
        "Salary",
    )

    create_transaction(
        client,
        token,
        "DEBIT",
        3000,
        "Food",
    )

    response = client.get(
        "/analytics/projected-cash-flow?days=30",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


# ============================================================
# MONTHLY ANALYTICS
# ============================================================

def test_monthly_analytics(client):

    token = register_user(
        client,
        "analytics-monthly@example.com",
    )

    create_transaction(
        client,
        token,
        "CREDIT",
        10000,
        "Salary",
    )

    create_transaction(
        client,
        token,
        "DEBIT",
        3000,
        "Food",
    )

    response = client.get(
        "/analytics/monthly?month=2026-08",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


# ============================================================
# SPENDING TRENDS
# ============================================================

def test_spending_trends(client):

    token = register_user(
        client,
        "analytics-trends@example.com",
    )

    response = client.get(
        "/analytics/trends?months=6",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


# ============================================================
# FINANCIAL SUMMARY
# ============================================================

def test_financial_summary(client):

    token = register_user(
        client,
        "analytics-summary@example.com",
    )

    create_transaction(
        client,
        token,
        "CREDIT",
        10000,
        "Salary",
    )

    create_transaction(
        client,
        token,
        "DEBIT",
        3000,
        "Food",
    )

    response = client.get(
        "/analytics/summary",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None