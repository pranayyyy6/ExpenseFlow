from jose import jwt

from app.core.security import (
    SECRET_KEY,
    ALGORITHM,
    create_access_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password():

    password = "TestPassword123!"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(
        password,
        hashed,
    )

    assert not verify_password(
        "WrongPassword123!",
        hashed,
    )


def test_create_access_token():

    user_id = 123

    token = create_access_token(
        user_id
    )

    assert token is not None
    assert isinstance(token, str)

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    assert payload["sub"] == "123"
    assert "exp" in payload