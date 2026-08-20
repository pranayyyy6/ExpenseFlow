def test_root(client):

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == (
        "Welcome to Smart Receipt Expense Tracker"
    )


def test_health(client):

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "OK"