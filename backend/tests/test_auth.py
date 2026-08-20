from app.models.user import User

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


def test_register_duplicate_email(client):

    payload = {
        "email": "duplicate@example.com",
        "password": "TestPassword123!",
        "full_name": "Duplicate User",
    }

    first_response = client.post(
        "/auth/register",
        json=payload,
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/auth/register",
        json=payload,
    )

    assert second_response.status_code == 400

    assert (
        second_response.json()["detail"]
        == "Email already registered"
    )

def test_login_wrong_password(client):

    register_response = client.post(
        "/auth/register",
        json={
            "email": "wrong-password@example.com",
            "password": "CorrectPassword123!",
            "full_name": "Wrong Password User",
        },
    )

    assert register_response.status_code == 200

    response = client.post(
        "/auth/login",
        json={
            "email": "wrong-password@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401

    assert (
        response.json()["detail"]
        == "Invalid email or password"
    )


def test_login_inactive_user(
    client,
    db_session,
):

    register_response = client.post(
        "/auth/register",
        json={
            "email": "inactive@example.com",
            "password": "TestPassword123!",
            "full_name": "Inactive User",
        },
    )

    assert register_response.status_code == 200

    user = (
        db_session.query(User)
        .filter(
            User.email == "inactive@example.com"
        )
        .first()
    )

    assert user is not None

    user.is_active = False

    db_session.commit()

    response = client.post(
        "/auth/login",
        json={
            "email": "inactive@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 403

    assert (
        response.json()["detail"]
        == "User account is inactive"
    )