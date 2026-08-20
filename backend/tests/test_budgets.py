# ============================================================
# TEST HELPERS
# ============================================================


def register_user(
    client,
    email,
):
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


def auth_header(token):
    return {
        "Authorization": f"Bearer {token}",
    }


def create_budget(
    client,
    token,
    category="Food",
    amount=5000,
    month="2026-08",
):
    return client.post(
        "/budgets/",
        headers=auth_header(token),
        json={
            "category": category,
            "amount": amount,
            "month": month,
        },
    )


def create_transaction(
    client,
    token,
    amount,
    category="Food",
    transaction_date="2026-08-12",
):
    return client.post(
        "/transactions/",
        headers=auth_header(token),
        json={
            "transaction_type": "DEBIT",
            "amount": amount,
            "category": category,
            "description": "Budget test expense",
            "merchant": "Test Merchant",
            "transaction_date": transaction_date,
            "payment_method": "UPI",
            "reference_id": f"BUDGET-{amount}-{category}",
        },
    )


# ============================================================
# CREATE
# ============================================================


def test_create_budget(client):

    token = register_user(
        client,
        "budget-create@example.com",
    )

    response = create_budget(
        client,
        token,
        amount=5000,
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


# ============================================================
# GET ALL
# ============================================================


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
        headers=auth_header(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "Food"


# ============================================================
# GET BY ID
# ============================================================


def test_get_budget_by_id(client):

    token = register_user(
        client,
        "budget-get@example.com",
    )

    created = create_budget(
        client,
        token,
    )

    assert created.status_code == 200

    budget_id = created.json()["id"]

    response = client.get(
        f"/budgets/{budget_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == budget_id
    assert data["category"] == "Food"
    assert data["amount"] == 5000
    assert data["month"] == "2026-08"


def test_get_nonexistent_budget_returns_404(client):

    token = register_user(
        client,
        "budget-not-found@example.com",
    )

    response = client.get(
        "/budgets/999999",
        headers=auth_header(token),
    )

    assert response.status_code == 404


# ============================================================
# AUTHENTICATION
# ============================================================


def test_budget_requires_authentication(client):

    response = client.get(
        "/budgets/"
    )

    assert response.status_code in (
        401,
        403,
    )


# ============================================================
# USER OWNERSHIP
# ============================================================


def test_user_cannot_access_another_users_budget(client):

    # --------------------------------------------------------
    # USER A
    # --------------------------------------------------------

    user_a_token = register_user(
        client,
        "budget-user-a@example.com",
    )

    create_response = create_budget(
        client,
        user_a_token,
    )

    assert create_response.status_code == 200

    budget_id = create_response.json()["id"]

    # --------------------------------------------------------
    # USER B
    # --------------------------------------------------------

    user_b_token = register_user(
        client,
        "budget-user-b@example.com",
    )

    response = client.get(
        f"/budgets/{budget_id}",
        headers=auth_header(user_b_token),
    )

    assert response.status_code == 404


# ============================================================
# UPDATE
# ============================================================


def test_update_budget_amount(client):

    token = register_user(
        client,
        "budget-update@example.com",
    )

    created = create_budget(
        client,
        token,
        amount=5000,
    )

    assert created.status_code == 200

    budget_id = created.json()["id"]

    response = client.put(
        f"/budgets/{budget_id}",
        headers=auth_header(token),
        json={
            "amount": 7500,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == 7500
    assert data["category"] == "Food"
    assert data["month"] == "2026-08"


def test_update_budget_category(client):

    token = register_user(
        client,
        "budget-update-category@example.com",
    )

    created = create_budget(
        client,
        token,
        category="Food",
    )

    assert created.status_code == 200

    budget_id = created.json()["id"]

    response = client.put(
        f"/budgets/{budget_id}",
        headers=auth_header(token),
        json={
            "category": "Shopping",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "Shopping"
    assert data["amount"] == 5000


def test_update_budget_month(client):

    token = register_user(
        client,
        "budget-update-month@example.com",
    )

    created = create_budget(
        client,
        token,
        month="2026-08",
    )

    assert created.status_code == 200

    budget_id = created.json()["id"]

    response = client.put(
        f"/budgets/{budget_id}",
        headers=auth_header(token),
        json={
            "month": "2026-09",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["month"] == "2026-09"
    assert data["category"] == "Food"


def test_update_budget_duplicate_is_rejected(client):

    token = register_user(
        client,
        "budget-update-duplicate@example.com",
    )

    first = create_budget(
        client,
        token,
        category="Food",
        month="2026-08",
    )

    second = create_budget(
        client,
        token,
        category="Shopping",
        month="2026-08",
    )

    assert first.status_code == 200
    assert second.status_code == 200

    second_id = second.json()["id"]

    response = client.put(
        f"/budgets/{second_id}",
        headers=auth_header(token),
        json={
            "category": "Food",
        },
    )

    assert response.status_code == 409


def test_update_nonexistent_budget_returns_404(client):

    token = register_user(
        client,
        "budget-update-not-found@example.com",
    )

    response = client.put(
        "/budgets/999999",
        headers=auth_header(token),
        json={
            "amount": 10000,
        },
    )

    assert response.status_code == 404


# ============================================================
# DELETE
# ============================================================


def test_delete_budget(client):

    token = register_user(
        client,
        "budget-delete@example.com",
    )

    created = create_budget(
        client,
        token,
    )

    assert created.status_code == 200

    budget_id = created.json()["id"]

    response = client.delete(
        f"/budgets/{budget_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["budget_id"] == budget_id
    assert "message" in data

    # --------------------------------------------------------
    # Verify deletion
    # --------------------------------------------------------

    get_response = client.get(
        f"/budgets/{budget_id}",
        headers=auth_header(token),
    )

    assert get_response.status_code == 404


def test_delete_nonexistent_budget_returns_404(client):

    token = register_user(
        client,
        "budget-delete-not-found@example.com",
    )

    response = client.delete(
        "/budgets/999999",
        headers=auth_header(token),
    )

    assert response.status_code == 404


# ============================================================
# BUDGET STATUS
# ============================================================


def test_budget_status_on_track(client):

    token = register_user(
        client,
        "budget-status-on-track@example.com",
    )

    created = create_budget(
        client,
        token,
        amount=10000,
        category="Food",
        month="2026-08",
    )

    assert created.status_code == 200

    budget_id = created.json()["id"]

    response = client.get(
        f"/budgets/{budget_id}/status",
        headers=auth_header(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["budget_id"] == budget_id
    assert data["category"] == "Food"
    assert data["month"] == "2026-08"
    assert data["budget"] == 10000
    assert data["spent"] == 0
    assert data["remaining"] == 10000
    assert data["utilization_percent"] == 0
    assert data["status"] == "ON_TRACK"


def test_budget_status_warning(client):

    token = register_user(
        client,
        "budget-status-warning@example.com",
    )

    created = create_budget(
        client,
        token,
        amount=10000,
        category="Food",
        month="2026-08",
    )

    assert created.status_code == 200

    budget_id = created.json()["id"]

    transaction = create_transaction(
        client,
        token,
        amount=8500,
        category="Food",
        transaction_date="2026-08-12",
    )

    assert transaction.status_code == 200

    response = client.get(
        f"/budgets/{budget_id}/status",
        headers=auth_header(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["budget_id"] == budget_id
    assert data["budget"] == 10000
    assert data["spent"] == 8500
    assert data["remaining"] == 1500
    assert data["utilization_percent"] == 85
    assert data["status"] == "WARNING"


def test_budget_status_exceeded(client):

    token = register_user(
        client,
        "budget-status-exceeded@example.com",
    )

    created = create_budget(
        client,
        token,
        amount=10000,
        category="Food",
        month="2026-08",
    )

    assert created.status_code == 200

    budget_id = created.json()["id"]

    transaction = create_transaction(
        client,
        token,
        amount=12000,
        category="Food",
        transaction_date="2026-08-12",
    )

    assert transaction.status_code == 200

    response = client.get(
        f"/budgets/{budget_id}/status",
        headers=auth_header(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["budget_id"] == budget_id
    assert data["budget"] == 10000
    assert data["spent"] == 12000
    assert data["remaining"] == -2000
    assert data["utilization_percent"] == 120
    assert data["status"] == "EXCEEDED"


def test_budget_status_not_found(client):

    token = register_user(
        client,
        "budget-status-not-found@example.com",
    )

    response = client.get(
        "/budgets/999999/status",
        headers=auth_header(token),
    )

    assert response.status_code == 404
# ============================================================
# BUDGET OVERVIEW
# ============================================================


def test_budget_overview_empty(client):

    token = register_user(
        client,
        "budget-overview-empty@example.com",
    )

    response = client.get(
        "/budgets/overview",
        params={
            "month": "2026-08",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["month"] == "2026-08"

    assert data["budgets"] == []

    assert data["summary"]["total_budget"] == 0
    assert data["summary"]["total_spent"] == 0
    assert data["summary"]["total_remaining"] == 0
    assert data["summary"]["on_track"] == 0
    assert data["summary"]["warning"] == 0
    assert data["summary"]["exceeded"] == 0


def test_budget_overview_on_track(client):

    token = register_user(
        client,
        "budget-overview-on-track@example.com",
    )

    created = create_budget(
        client,
        token,
        category="Food",
        amount=10000,
        month="2026-08",
    )

    assert created.status_code == 200

    transaction = create_transaction(
        client,
        token,
        amount=3000,
        category="Food",
        transaction_date="2026-08-10",
    )

    assert transaction.status_code == 200

    response = client.get(
        "/budgets/overview",
        params={
            "month": "2026-08",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["month"] == "2026-08"

    assert len(data["budgets"]) == 1

    budget = data["budgets"][0]

    assert budget["category"] == "Food"
    assert budget["budget"] == 10000
    assert budget["spent"] == 3000
    assert budget["remaining"] == 7000
    assert budget["utilization_percent"] == 30
    assert budget["status"] == "ON_TRACK"

    summary = data["summary"]

    assert summary["total_budget"] == 10000
    assert summary["total_spent"] == 3000
    assert summary["total_remaining"] == 7000
    assert summary["on_track"] == 1
    assert summary["warning"] == 0
    assert summary["exceeded"] == 0


def test_budget_overview_warning(client):

    token = register_user(
        client,
        "budget-overview-warning@example.com",
    )

    created = create_budget(
        client,
        token,
        category="Food",
        amount=10000,
        month="2026-08",
    )

    assert created.status_code == 200

    transaction = create_transaction(
        client,
        token,
        amount=8500,
        category="Food",
        transaction_date="2026-08-10",
    )

    assert transaction.status_code == 200

    response = client.get(
        "/budgets/overview",
        params={
            "month": "2026-08",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["budgets"]) == 1

    budget = data["budgets"][0]

    assert budget["budget"] == 10000
    assert budget["spent"] == 8500
    assert budget["remaining"] == 1500
    assert budget["utilization_percent"] == 85
    assert budget["status"] == "WARNING"

    summary = data["summary"]

    assert summary["total_budget"] == 10000
    assert summary["total_spent"] == 8500
    assert summary["total_remaining"] == 1500
    assert summary["on_track"] == 0
    assert summary["warning"] == 1
    assert summary["exceeded"] == 0


def test_budget_overview_exceeded(client):

    token = register_user(
        client,
        "budget-overview-exceeded@example.com",
    )

    created = create_budget(
        client,
        token,
        category="Food",
        amount=10000,
        month="2026-08",
    )

    assert created.status_code == 200

    transaction = create_transaction(
        client,
        token,
        amount=12000,
        category="Food",
        transaction_date="2026-08-10",
    )

    assert transaction.status_code == 200

    response = client.get(
        "/budgets/overview",
        params={
            "month": "2026-08",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["budgets"]) == 1

    budget = data["budgets"][0]

    assert budget["budget"] == 10000
    assert budget["spent"] == 12000
    assert budget["remaining"] == -2000
    assert budget["utilization_percent"] == 120
    assert budget["status"] == "EXCEEDED"

    summary = data["summary"]

    assert summary["total_budget"] == 10000
    assert summary["total_spent"] == 12000
    assert summary["total_remaining"] == -2000
    assert summary["on_track"] == 0
    assert summary["warning"] == 0
    assert summary["exceeded"] == 1


def test_budget_overview_multiple_categories(client):

    token = register_user(
        client,
        "budget-overview-multiple@example.com",
    )

    food = create_budget(
        client,
        token,
        category="Food",
        amount=10000,
        month="2026-08",
    )

    shopping = create_budget(
        client,
        token,
        category="Shopping",
        amount=5000,
        month="2026-08",
    )

    assert food.status_code == 200
    assert shopping.status_code == 200

    food_transaction = create_transaction(
        client,
        token,
        amount=3000,
        category="Food",
        transaction_date="2026-08-10",
    )

    shopping_transaction = create_transaction(
        client,
        token,
        amount=4500,
        category="Shopping",
        transaction_date="2026-08-11",
    )

    assert food_transaction.status_code == 200
    assert shopping_transaction.status_code == 200

    response = client.get(
        "/budgets/overview",
        params={
            "month": "2026-08",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["budgets"]) == 2

    summary = data["summary"]

    assert summary["total_budget"] == 15000
    assert summary["total_spent"] == 7500
    assert summary["total_remaining"] == 7500

    assert summary["on_track"] == 1
    assert summary["warning"] == 1
    assert summary["exceeded"] == 0