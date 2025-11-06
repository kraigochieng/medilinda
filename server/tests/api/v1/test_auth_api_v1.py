import pytest
from fastapi import status


@pytest.fixture
def sample_user_signup_payload():
    """User signup payload"""
    return {
        "username": "kraig",
        "first_name": "Kraig",
        "last_name": "Ochieng",
        "password": "mypassword",
    }


@pytest.fixture
def sample_login_form():
    """Form data for login"""
    return {
        "username": "kraig",
        "password": "mypassword",
    }


def test_signup_user(client, sample_user_signup_payload):
    """POST /api/v1/auth/signup - create a new user"""
    response = client.post("/api/v1/auth/signup", json=sample_user_signup_payload)
    print(response.json())
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "id" in data
    assert data["username"] == sample_user_signup_payload["username"]


def test_signup_existing_username(client, sample_user_signup_payload):
    """POST /api/v1/auth/signup - duplicate username should fail"""
    client.post("/api/v1/auth/signup", json=sample_user_signup_payload)
    response = client.post("/api/v1/auth/signup", json=sample_user_signup_payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_login_user_success(client, sample_user_signup_payload, sample_login_form):
    """POST /api/v1/auth/token - successful login"""
    # create user first
    client.post("/api/v1/auth/signup", json=sample_user_signup_payload)

    response = client.post(
        "/api/v1/auth/token",
        data=sample_login_form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_user_incorrect_username(client, sample_login_form):
    """POST /api/v1/auth/token - wrong username"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "nonexistent", "password": "irrelevant"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_user_incorrect_password(client, sample_user_signup_payload):
    """POST /api/v1/auth/token - wrong password"""
    # create user
    client.post("/api/v1/auth/signup", json=sample_user_signup_payload)

    response = client.post(
        "/api/v1/auth/token",
        data={"username": "kraig", "password": "wrongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
