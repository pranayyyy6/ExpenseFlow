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