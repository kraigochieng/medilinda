# server/api/v1/auth_api_v1.py

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from server.basemodels.auth import Token
from server.basemodels.user import UserSignupBaseModel, UserDetailsBaseModel
from server.dependencies import get_db
from server.repositories.auth import AuthRepository
from server.services.auth import AuthService
from fastapi import status

router = APIRouter(prefix="/api/v1/auth", tags=["auth", "v1"])


def get_auth_service(db: Session = Depends(get_db)):
    repo = AuthRepository(db)
    return AuthService(repo)


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthService = Depends(get_auth_service),
):
    return service.login(form_data.username, form_data.password)


@router.post(
    "/signup", response_model=UserDetailsBaseModel, status_code=status.HTTP_200_OK
)
async def signup(
    user: UserSignupBaseModel,
    service: AuthService = Depends(get_auth_service),
):
    return service.signup(user)
