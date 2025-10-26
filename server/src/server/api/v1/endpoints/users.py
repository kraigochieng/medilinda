from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, load_only

from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.models.user import UserModel
from server.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/users", tags=["users", "v1"])


@router.get("/me", status_code=status.HTTP_200_OK)
async def read_users_me(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    db_user = (
        db.query(UserModel)
        .options(
            load_only(
                UserModel.id,
                UserModel.username,
                UserModel.first_name,
                UserModel.last_name,
            )
        )
        .filter(UserModel.username == current_user.username)
        .first()
    )

    return db_user
