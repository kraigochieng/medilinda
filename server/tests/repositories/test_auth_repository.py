import pytest
from server.models.user import UserModel
from server.repositories.auth import AuthRepository


@pytest.fixture
def auth_repository(db):
    """Use real repository connected to test DB."""
    return AuthRepository(db)


@pytest.fixture
def sample_user_data():
    return {
        "username": "kraig",
        "password": "hashedpassword",
        "first_name": "Kraig",
        "last_name": "Ochieng",
    }


def test_create_user(auth_repository, sample_user_data):
    user_model = UserModel(**sample_user_data)
    created_user = auth_repository.create_user(
        user_model, hashed_password="hashedpassword"
    )

    assert created_user.username == sample_user_data["username"]
    assert created_user.id is not None


def test_get_user_by_username(auth_repository, sample_user_data):
    # Add directly
    user = UserModel(**sample_user_data)

    auth_repository.create_user(user, hashed_password="hashedpassword")

    fetched_user = auth_repository.get_user_by_username(sample_user_data["username"])

    assert fetched_user is not None
    assert fetched_user.username == sample_user_data["username"]
