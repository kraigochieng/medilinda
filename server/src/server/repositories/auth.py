from server.basemodels.user import UserSignupBaseModel
from server.models.user import UserModel
from sqlalchemy.orm import Session


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def create_user(self, user: UserSignupBaseModel, hashed_password: str) -> UserModel:
        new_user = UserModel(
            username=user.username,
            password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user
