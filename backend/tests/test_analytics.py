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