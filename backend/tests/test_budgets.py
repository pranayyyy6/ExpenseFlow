def register_user(client, email):

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": "Budget User",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_budget(client, token):

    response = client.post(
        "/budgets/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "category": "Food",
            "amount": 5000,
            "month": "2026-08",
        },
    )

    return response


def test_create_budget(client):

    token = register_user(
        client,
        "budget-create@example.com",
    )

    response = create_budget(
        client,
        token,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "Food"
    assert data["amount"] == 5000
    assert data["month"] == "2026-08"


def test_duplicate_budget_is_rejected(client):

    token = register_user(
        client,
        "budget-duplicate@example.com",
    )

    first = create_budget(
        client,
        token,
    )

    assert first.status_code == 200

    second = create_budget(
        client,
        token,
    )

    assert second.status_code == 409


def test_get_budgets(client):

    token = register_user(
        client,
        "budget-list@example.com",
    )

    create_budget(
        client,
        token,
    )

    response = client.get(
        "/budgets/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "Food"


def test_budget_requires_authentication(client):

    response = client.get(
        "/budgets/"
    )

    assert response.status_code in (
        401,
        403,
    )


def test_user_cannot_access_another_users_budget(
    client,
):

    # ========================================================
    # USER A
    # ========================================================

    user_a_token = register_user(
        client,
        "budget-user-a@example.com",
    )

    create_response = create_budget(
        client,
        user_a_token,
    )

    assert create_response.status_code == 200

    budget_id = (
        create_response.json()["id"]
    )

    # ========================================================
    # USER B
    # ========================================================

    user_b_token = register_user(
        client,
        "budget-user-b@example.com",
    )

    response = client.get(
        f"/budgets/{budget_id}",
        headers={
            "Authorization": (
                f"Bearer {user_b_token}"
            ),
        },
    )

    assert response.status_code == 404