from datetime import timedelta

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from server.basemodels.auth import Token
from server.basemodels.user import UserDetailsBaseModel, UserSignupBaseModel
from server.exceptions import UserAlreadyExistsError
from server.repositories.auth import AuthRepository
from server.settings import settings
from server.utils.auth import (
    create_access_token,
    get_password_hash,
    verify_password,
)


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    def login(self, username: str, password: str) -> Token:
        user = self.repository.get_user_by_username(username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(
            minutes=settings.server_access_token_expire_minutes
        )

        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires,
        )

        return Token(access_token=access_token, token_type="bearer")

    def signup(self, user: UserSignupBaseModel) -> UserDetailsBaseModel:
        existing_user = self.repository.get_user_by_username(user.username)

        if existing_user:
            raise UserAlreadyExistsError(
                f"User with username {user.username} already exists"
            )

        hashed_password = get_password_hash(user.password)
        new_user = self.repository.create_user(user, hashed_password)

        user_basemodel = UserDetailsBaseModel(
            id=new_user.id,
            username=new_user.username,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
        )

        return user_basemodel
