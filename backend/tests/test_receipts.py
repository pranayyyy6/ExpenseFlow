def register_user(client, email):

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": "Receipt User",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_receipt(client, token):

    response = client.post(
        "/receipts/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "store_name": "DMart",
            "receipt_date": "2026-08-12",
            "total_amount": 1250,
            "image_path": None,
        },
    )

    return response


# ============================================================
# CREATE
# ============================================================

def test_create_receipt(client):

    token = register_user(
        client,
        "receipt-create@example.com",
    )

    response = create_receipt(
        client,
        token,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["store_name"] == "DMart"
    assert data["total_amount"] == 1250
    assert data["receipt_date"] == "2026-08-12"


# ============================================================
# GET ALL
# ============================================================

def test_get_receipts(client):

    token = register_user(
        client,
        "receipt-list@example.com",
    )

    create_response = create_receipt(
        client,
        token,
    )

    assert create_response.status_code == 200

    response = client.get(
        "/receipts/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["store_name"] == "DMart"


# ============================================================
# AUTHENTICATION
# ============================================================

def test_receipts_require_authentication(client):

    response = client.get(
        "/receipts/"
    )

    assert response.status_code in (
        401,
        403,
    )


# ============================================================
# GET BY ID
# ============================================================

def test_get_receipt_by_id(client):

    token = register_user(
        client,
        "receipt-id@example.com",
    )

    create_response = create_receipt(
        client,
        token,
    )

    assert create_response.status_code == 200

    receipt_id = (
        create_response.json()["id"]
    )

    response = client.get(
        f"/receipts/{receipt_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == receipt_id
    assert data["store_name"] == "DMart"

    # Receipt response should expose items.
    assert "items" in data
    assert isinstance(
        data["items"],
        list,
    )


# ============================================================
# USER ISOLATION
# ============================================================

def test_user_cannot_access_another_users_receipt(
    client,
):

    # --------------------------------------------------------
    # USER A
    # --------------------------------------------------------

    user_a_token = register_user(
        client,
        "receipt-user-a@example.com",
    )

    create_response = create_receipt(
        client,
        user_a_token,
    )

    assert create_response.status_code == 200

    receipt_id = (
        create_response.json()["id"]
    )

    # --------------------------------------------------------
    # USER B
    # --------------------------------------------------------

    user_b_token = register_user(
        client,
        "receipt-user-b@example.com",
    )

    response = client.get(
        f"/receipts/{receipt_id}",
        headers={
            "Authorization": (
                f"Bearer {user_b_token}"
            ),
        },
    )

    # User B must not be able to see
    # User A's receipt.

    assert response.status_code == 404


# ============================================================
# DELETE
# ============================================================

def test_delete_receipt(client):

    token = register_user(
        client,
        "receipt-delete@example.com",
    )

    create_response = create_receipt(
        client,
        token,
    )

    assert create_response.status_code == 200

    receipt_id = (
        create_response.json()["id"]
    )

    response = client.delete(
        f"/receipts/{receipt_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    # Verify it no longer exists.

    get_response = client.get(
        f"/receipts/{receipt_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert get_response.status_code == 404