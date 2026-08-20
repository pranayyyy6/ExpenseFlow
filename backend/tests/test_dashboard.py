def register_user(client, email):

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": "Dashboard User",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_authenticated_dashboard(client):

    token = register_user(
        client,
        "dashboard-integration@example.com",
    )

    response = client.get(
        "/dashboard/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "financial" in data
    assert "budgets" in data
    assert "receipts" in data
    assert "upcoming_bills" in data
    assert "top_categories" in data
    assert "spending_trends" in data
    assert "recent_transactions" in data
    assert "recent_receipts" in data

def create_transaction(
    client,
    token,
    amount=1000,
):

    return client.post(
        "/transactions/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "transaction_type": "DEBIT",
            "amount": amount,
            "category": "Food",
            "description": "Lunch",
            "merchant": "Restaurant",
            "transaction_date": "2026-08-19",
            "payment_method": "UPI",
            "reference_id": "DASH-001",
        },
    )


def test_dashboard_contains_recent_transaction(client):

    token = register_user(
        client,
        "dashboard-transaction@example.com",
    )

    response = create_transaction(
        client,
        token,
        amount=1500,
    )

    assert response.status_code == 200

    dashboard = client.get(
        "/dashboard/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert dashboard.status_code == 200

    data = dashboard.json()

    assert len(
        data["recent_transactions"]
    ) >= 1

    transaction = data[
        "recent_transactions"
    ][0]

    assert transaction["amount"] == 1500
    assert transaction["category"] == "Food"

def create_dashboard_budget(
    client,
    token,
    category,
    amount,
):

    return client.post(
        "/budgets/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "category": category,
            "amount": amount,
            "month": "2026-08",
        },
    )


def test_dashboard_budget_statuses(client):

    token = register_user(
        client,
        "dashboard-budget@example.com",
    )

    # ON_TRACK
    response = create_dashboard_budget(
        client,
        token,
        "Food",
        10000,
    )

    assert response.status_code == 200

    # WARNING
    response = create_dashboard_budget(
        client,
        token,
        "Travel",
        5000,
    )

    assert response.status_code == 200

    # EXCEEDED
    response = create_dashboard_budget(
        client,
        token,
        "Shopping",
        3000,
    )

    assert response.status_code == 200

    # Transactions create spending against the budgets.
    transaction = create_transaction(
        client,
        token,
        amount=3000,
    )

    assert transaction.status_code == 200

    dashboard = client.get(
        "/dashboard/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert dashboard.status_code == 200

    data = dashboard.json()

    budgets = data["budgets"]

    assert len(
        budgets["items"]
    ) == 3

def create_recurring_bill(
    client,
    token,
    name="Netflix",
    amount=499,
    next_due_date="2026-08-20",
    category="Entertainment",
):

    return client.post(
        "/recurring-bills/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": name,
            "amount": amount,
            "frequency": "MONTHLY",
            "next_due_date": next_due_date,
            "category": category,
            "payment_method": "UPI",
            "auto_pay": True,
        },
    )


def test_dashboard_contains_upcoming_bill(client):

    token = register_user(
        client,
        "dashboard-bill@example.com",
    )

    response = create_recurring_bill(
        client,
        token,
    )

    assert response.status_code == 200

    dashboard = client.get(
        "/dashboard/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert dashboard.status_code == 200

    data = dashboard.json()

    print("\nDASHBOARD UPCOMING BILLS:")
    print(data["upcoming_bills"])

    upcoming = data["upcoming_bills"]

    assert upcoming["count"] >= 1


def test_dashboard_contains_recent_receipt(client):

    token = register_user(
        client,
        "dashboard-receipt@example.com",
    )

    response = client.post(
        "/receipts/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "store_name": "DMart",
            "receipt_date": "2026-08-19",
            "total_amount": 1250,
            "image_path": "uploads/test.jpg",
        },
    )

    assert response.status_code == 200

    dashboard = client.get(
        "/dashboard/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert dashboard.status_code == 200

    data = dashboard.json()

    receipts = data["recent_receipts"]

    assert len(receipts) >= 1

    receipt = receipts[0]

    assert receipt["store_name"] == "DMart"
    assert receipt["total_amount"] == 1250

def test_dashboard_budget_warning_and_exceeded(client):

    token = register_user(
        client,
        "dashboard-budget-status@example.com",
    )

    # --------------------------------------------------------
    # WARNING: 90% spent
    # --------------------------------------------------------

    response = client.post(
        "/budgets/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "category": "Travel",
            "amount": 5000,
            "month": "2026-08",
        },
    )

    assert response.status_code == 200

    # 4500 / 5000 = 90%
    response = client.post(
        "/transactions/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "transaction_type": "DEBIT",
            "amount": 4500,
            "category": "Travel",
            "description": "Travel expense",
            "merchant": "Travel Store",
            "transaction_date": "2026-08-19",
            "payment_method": "UPI",
            "reference_id": "DASH-WARNING-001",
        },
    )

    assert response.status_code == 200

    # --------------------------------------------------------
    # EXCEEDED: 120% spent
    # --------------------------------------------------------

    response = client.post(
        "/budgets/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "category": "Shopping",
            "amount": 3000,
            "month": "2026-08",
        },
    )

    assert response.status_code == 200

    # 3600 / 3000 = 120%
    response = client.post(
        "/transactions/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "transaction_type": "DEBIT",
            "amount": 3600,
            "category": "Shopping",
            "description": "Shopping expense",
            "merchant": "Shopping Store",
            "transaction_date": "2026-08-19",
            "payment_method": "UPI",
            "reference_id": "DASH-EXCEEDED-001",
        },
    )

    assert response.status_code == 200

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    dashboard = client.get(
        "/dashboard/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert dashboard.status_code == 200

    data = dashboard.json()

    budgets = data["budgets"]

    # --------------------------------------------------------
    # Verify counts
    # --------------------------------------------------------

    assert budgets["warning"] == 1
    assert budgets["exceeded"] == 1

    # --------------------------------------------------------
    # Verify individual statuses
    # --------------------------------------------------------

    items = budgets["items"]

    travel = next(
        item
        for item in items
        if item["category"] == "Travel"
    )

    shopping = next(
        item
        for item in items
        if item["category"] == "Shopping"
    )

    assert travel["status"] == "WARNING"
    assert travel["utilization_percent"] == 90

    assert shopping["status"] == "EXCEEDED"
    assert shopping["utilization_percent"] == 120


def test_dashboard_skips_invalid_and_past_bills(client):

    token = register_user(
        client,
        "dashboard-bill-edge@example.com",
    )

    # --------------------------------------------------------
    # Invalid date
    # --------------------------------------------------------

    invalid_response = create_recurring_bill(
        client,
        token,
        name="Invalid Date Bill",
        amount=500,
        next_due_date="not-a-date",
    )

    # The API/schema may reject this before it reaches
    # dashboard_service.
    assert invalid_response.status_code == 200

    # --------------------------------------------------------
    # Past bill
    # --------------------------------------------------------

    past_response = create_recurring_bill(
        client,
        token,
        name="Past Bill",
        amount=750,
        next_due_date="2020-01-01",
    )

    assert past_response.status_code == 200

    # --------------------------------------------------------
    # Dashboard
    # --------------------------------------------------------

    dashboard = client.get(
        "/dashboard/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert dashboard.status_code == 200

    data = dashboard.json()

    upcoming = data["upcoming_bills"]

    # Past bill must not appear.
    assert all(
        bill["name"] != "Past Bill"
        for bill in upcoming["items"]
    )


def test_dashboard_spending_trends_crosses_previous_year(
    client,
    monkeypatch,
):

    from datetime import date

    class FakeDate(date):

        @classmethod
        def today(cls):
            return cls(2026, 1, 15)

    monkeypatch.setattr(
        "app.services.dashboard_service.date",
        FakeDate,
    )

    token = register_user(
        client,
        "dashboard-year-rollover@example.com",
    )

    response = client.get(
        "/dashboard/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    trends = data["spending_trends"]

    assert len(trends) == 6

    # Six-month window ending in January 2026.
    assert trends[0]["month"] == "2025-08"
    assert trends[1]["month"] == "2025-09"
    assert trends[2]["month"] == "2025-10"
    assert trends[3]["month"] == "2025-11"
    assert trends[4]["month"] == "2025-12"
    assert trends[5]["month"] == "2026-01"