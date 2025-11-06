# import pytest
# from fastapi import HTTPException, status
# from server.basemodels.user import UserSignupBaseModel
# from server.models.user import UserModel
# from server.repositories.auth import AuthRepository
# from server.services.auth import AuthService


# @pytest.fixture
# def auth_repository(db):
#     """Use real repository connected to test DB."""
#     return AuthRepository(db)


# @pytest.fixture
# def auth_service(auth_repository):
#     """Wrap repository in the service layer."""
#     return AuthService(auth_repository)


# @pytest.fixture
# def sample_signup_data():
#     """Valid user signup payload."""
#     return UserSignupBaseModel(
#         username="kraig",
#         first_name="Kraig",
#         last_name="Ochieng",
#         password="mypassword",
#     )


# def test_signup_creates_user(auth_service, auth_repository, db, sample_signup_data):
#     """Ensure signup inserts new user into the DB."""
#     response = auth_service.signup(sample_signup_data)
#     assert response.status_code == status.HTTP_200_OK

#     # verify it’s actually in the DB
#     user_in_db = (
#         db.query(UserModel).filter_by(username=sample_signup_data.username).first()
#     )
#     assert user_in_db is not None
#     assert user_in_db.first_name == "Kraig"
#     assert user_in_db.last_name == "Ochieng"


# def test_signup_raises_if_user_exists(auth_service, db, sample_signup_data):
#     """Duplicate username raises 400 error."""
#     # Create first user
#     auth_service.signup(sample_signup_data)

#     # Try again
#     with pytest.raises(HTTPException) as exc:
#         auth_service.signup(sample_signup_data)

#     assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
#     assert "exists" in exc.value.detail


# def test_login_success(auth_service, db, sample_signup_data):
#     """Login works with correct username/password."""
#     auth_service.signup(sample_signup_data)

#     token_response = auth_service.login(
#         username=sample_signup_data.username,
#         password=sample_signup_data.password,
#     )
#     assert token_response.status_code == status.HTTP_200_OK
#     data = token_response.body.decode()
#     assert "access_token" in data


# def test_login_invalid_username(auth_service):
#     """Login with non-existent username raises 401."""
#     with pytest.raises(HTTPException) as exc:
#         auth_service.login("nope", "password")
#     assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
#     assert "Incorrect username" in exc.value.detail


# def test_login_invalid_password(auth_service, sample_signup_data):
#     """Login with wrong password raises 401."""
#     # Create user with correct password
#     auth_service.signup(sample_signup_data)

#     # Wrong password
#     with pytest.raises(HTTPException) as exc:
#         auth_service.login(sample_signup_data.username, "wrongpassword")

#     assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
#     assert "Incorrect password" in exc.value.detail
