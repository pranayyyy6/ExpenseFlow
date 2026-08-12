def register_user(
    client,
    email,
):
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": "Test User",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_transaction(
    client,
    token,
):
    response = client.post(
        "/transactions/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "transaction_type": "DEBIT",
            "amount": 1000,
            "category": "Food",
            "description": "Lunch",
            "merchant": "Restaurant",
            "transaction_date": "2026-08-12",
            "payment_method": "UPI",
            "reference_id": "TEST-001",
        },
    )

    return response


def test_create_transaction(client):

    token = register_user(
        client,
        "transaction@example.com",
    )

    response = create_transaction(
        client,
        token,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == 1000
    assert data["category"] == "Food"
    assert data["transaction_type"] == "DEBIT"


def test_get_transactions_only_returns_current_users_data(
    client,
):

    token = register_user(
        client,
        "list@example.com",
    )

    create_response = create_transaction(
        client,
        token,
    )

    assert create_response.status_code == 200

    response = client.get(
        "/transactions/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["amount"] == 1000


def test_transaction_requires_authentication(
    client,
):

    response = client.get(
        "/transactions/"
    )

    assert response.status_code in (
        401,
        403,
    )


def test_user_cannot_access_another_users_transaction(
    client,
):

    # ========================================================
    # USER A
    # ========================================================

    user_a_token = register_user(
        client,
        "usera@example.com",
    )

    transaction_response = create_transaction(
        client,
        user_a_token,
    )

    assert transaction_response.status_code == 200

    transaction = (
        transaction_response.json()
    )

    transaction_id = transaction["id"]

    # ========================================================
    # USER B
    # ========================================================

    user_b_token = register_user(
        client,
        "userb@example.com",
    )

    response = client.get(
        f"/transactions/{transaction_id}",
        headers={
            "Authorization": (
                f"Bearer {user_b_token}"
            ),
        },
    )

    # User B must NOT see User A's transaction.

    assert response.status_code == 404