def test_register(client):

    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login(client):

    register_response = client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "TestPassword123!",
            "full_name": "Login User",
        },
    )

    assert register_response.status_code == 200

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_login(client):

    response = client.post(
        "/auth/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401