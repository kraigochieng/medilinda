from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt

from server.basemodels.auth import Token
from server.basemodels.user import UserDetailsBaseModel, UserSignupBaseModel
from server.settings import settings
from server.dependencies import get_db
from server.models.user import UserModel
from server.services.auth import (
    create_access_token,
    # create_refresh_token,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth", "v1"])


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    existing_user = (
        db.query(UserModel).filter(UserModel.username == form_data.username).first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, existing_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=settings.server_access_token_expire_minutes
    )

    
    access_token = create_access_token(
        data={"sub": existing_user.username}, expires_delta=access_token_expires
    )

    # refresh_token_expires = datetime.timedelta(
    #     days=settings.server_refresh_token_expire_days
    # )

    # refresh_token = create_refresh_token(
    #     data={"sub": existing_user.username}, expires_delta=refresh_token_expires
    # )

    return JSONResponse(
        content=jsonable_encoder(
            {
                "access_token": access_token,
                # "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        ),
        status_code=status.HTTP_200_OK,
    )


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserSignupBaseModel, db: Session = Depends(get_db)):
    existing_user = (
        db.query(UserModel).filter(UserModel.username == user.username).first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    new_user = UserModel(
        username=user.username,
        password=get_password_hash(user.username),
        first_name=user.first_name,
        last_name=user.last_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user_basemodel = UserDetailsBaseModel(
        id=new_user.id,
        username=new_user.username,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
    )
    return JSONResponse(
        content=jsonable_encoder(user_basemodel), status_code=status.HTTP_200_OK
    )


# @router.post("/token/refresh", status_code=status.HTTP_201_CREATED)
# async def refresh_access_token(refresh_token: str):
#     try:
#         payload = jwt.decode(
#             refresh_token,
#             settings.server_refresh_secret_key,
#             algorithms=[settings.server_refresh_algorithm],
#         )
#         username = payload.get("sub")

#         if username is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
#             )

#         # Generate new access token
#         new_access_token = create_access_token(
#             data={"sub": username},
#             expires_delta=datetime.timedelta(
#                 minutes=settings.server_access_token_expire_minutes
#             ),
#         )
#         return {"access_token": new_access_token, "token_type": "bearer"}

#     except jwt.ExpiredSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
#         )
#     except jwt.JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
#         )
