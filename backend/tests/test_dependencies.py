from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt

from app.core.dependencies import get_current_user
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User


def test_invalid_jwt_token(db_session):

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="this-is-not-a-valid-jwt",
    )

    try:
        get_current_user(
            credentials=credentials,
            db=db_session,
        )

        assert False, "Expected HTTPException"

    except HTTPException as exc:
        assert exc.status_code == 401
        assert (
            exc.detail
            == "Invalid or expired authentication token"
        )


def test_jwt_without_sub(db_session):

    token = jwt.encode(
        {
            "some_field": "some_value",
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    try:
        get_current_user(
            credentials=credentials,
            db=db_session,
        )

        assert False, "Expected HTTPException"

    except HTTPException as exc:
        assert exc.status_code == 401
        assert (
            exc.detail
            == "Invalid authentication token"
        )


def test_user_not_found(db_session):

    token = jwt.encode(
        {
            "sub": "999999",
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    try:
        get_current_user(
            credentials=credentials,
            db=db_session,
        )

        assert False, "Expected HTTPException"

    except HTTPException as exc:
        assert exc.status_code == 401
        assert (
            exc.detail
            == "User not found"
        )


def test_inactive_user(db_session):

    user = User(
        email="inactive-dependency@example.com",
        password_hash="test-hash",
        full_name="Inactive User",
        is_active=False,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = jwt.encode(
        {
            "sub": str(user.id),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    try:
        get_current_user(
            credentials=credentials,
            db=db_session,
        )

        assert False, "Expected HTTPException"

    except HTTPException as exc:
        assert exc.status_code == 403
        assert (
            exc.detail
            == "User account is inactive"
        )

def test_get_current_user_success(db_session):

    user = User(
        email="active-dependency@example.com",
        password_hash="test-hash",
        full_name="Active User",
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = jwt.encode(
        {
            "sub": str(user.id),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    result = get_current_user(
        credentials=credentials,
        db=db_session,
    )

    assert result.id == user.id
    assert result.email == "active-dependency@example.com"
    assert result.is_active is True