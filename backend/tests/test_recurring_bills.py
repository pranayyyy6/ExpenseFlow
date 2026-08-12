def register_user(client, email):

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": "Bill User",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_bill(client, token):

    response = client.post(
        "/recurring-bills/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Netflix",
            "amount": 649,
            "frequency": "MONTHLY",
            "next_due_date": "2026-08-20",
            "category": "Entertainment",
            "payment_method": "CARD",
            "auto_pay": True,
        },
    )

    return response


# ============================================================
# CREATE
# ============================================================

def test_create_recurring_bill(client):

    token = register_user(
        client,
        "bill-create@example.com",
    )

    response = create_bill(
        client,
        token,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Netflix"
    assert data["amount"] == 649
    assert data["frequency"] == "MONTHLY"


# ============================================================
# GET ALL
# ============================================================

def test_get_recurring_bills(client):

    token = register_user(
        client,
        "bill-list@example.com",
    )

    create_response = create_bill(
        client,
        token,
    )

    assert create_response.status_code == 200

    response = client.get(
        "/recurring-bills/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Netflix"


# ============================================================
# AUTHENTICATION
# ============================================================

def test_recurring_bills_require_authentication(
    client,
):

    response = client.get(
        "/recurring-bills/"
    )

    assert response.status_code in (
        401,
        403,
    )


# ============================================================
# GET BY ID
# ============================================================

def test_get_recurring_bill_by_id(client):

    token = register_user(
        client,
        "bill-id@example.com",
    )

    create_response = create_bill(
        client,
        token,
    )

    assert create_response.status_code == 200

    bill_id = (
        create_response.json()["id"]
    )

    response = client.get(
        f"/recurring-bills/{bill_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == bill_id
    assert data["name"] == "Netflix"


# ============================================================
# UPCOMING BILLS
# ============================================================

def test_upcoming_bills(client):

    token = register_user(
        client,
        "bill-upcoming@example.com",
    )

    create_response = create_bill(
        client,
        token,
    )

    assert create_response.status_code == 200

    response = client.get(
        "/recurring-bills/upcoming?days=30",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["total_upcoming"] == 649

    assert (
        data["upcoming_bills"][0]["name"]
        == "Netflix"
    )


# ============================================================
# USER ISOLATION
# ============================================================

def test_user_cannot_access_another_users_bill(
    client,
):

    # --------------------------------------------------------
    # USER A
    # --------------------------------------------------------

    user_a_token = register_user(
        client,
        "bill-user-a@example.com",
    )

    create_response = create_bill(
        client,
        user_a_token,
    )

    assert create_response.status_code == 200

    bill_id = (
        create_response.json()["id"]
    )

    # --------------------------------------------------------
    # USER B
    # --------------------------------------------------------

    user_b_token = register_user(
        client,
        "bill-user-b@example.com",
    )

    response = client.get(
        f"/recurring-bills/{bill_id}",
        headers={
            "Authorization": (
                f"Bearer {user_b_token}"
            ),
        },
    )

    assert response.status_code == 404


# ============================================================
# DELETE
# ============================================================

def test_delete_recurring_bill(client):

    token = register_user(
        client,
        "bill-delete@example.com",
    )

    create_response = create_bill(
        client,
        token,
    )

    assert create_response.status_code == 200

    bill_id = (
        create_response.json()["id"]
    )

    response = client.delete(
        f"/recurring-bills/{bill_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    get_response = client.get(
        f"/recurring-bills/{bill_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert get_response.status_code == 404