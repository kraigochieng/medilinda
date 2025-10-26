import pytest
from server.models.user import UserModel
from server.repositories.user import UserRepository


@pytest.fixture
def user_repository(db):
    """Fixture for UserRepository."""
    return UserRepository(db)


@pytest.fixture
def sample_user():
    """Fixture for a sample user record."""
    return UserModel(
        username="john_doe",
        password="hashedpassword123",
        first_name="John",
        last_name="Doe",
        disabled=False,
    )


def test_get_by_username_existing(user_repository, db, sample_user):
    """Test retrieving an existing user by username."""
    db.add(sample_user)
    db.commit()
    db.refresh(sample_user)

    fetched = user_repository.get_by_username("john_doe")

    assert fetched is not None
    assert fetched.username == "john_doe"
    assert fetched.password == "hashedpassword123"
    assert fetched.first_name == "John"
    assert fetched.last_name == "Doe"
    assert fetched.disabled is False


def test_get_by_username_nonexistent(user_repository):
    """Test retrieving a non-existent user returns None."""
    fetched = user_repository.get_by_username("nonexistent_user")
    assert fetched is None
