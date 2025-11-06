from server.basemodels.user import UserSignupBaseModel
from server.exceptions import ResourceNotFoundError
from server.models.user import UserModel
from sqlalchemy.orm import Session


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> UserModel:
        model = self.db.query(UserModel).filter(UserModel.username == username).first()

        # if not model:
        #     raise ResourceNotFoundError(f"User with username {username} not found")

        return model

    def create_user(self, user: UserSignupBaseModel, hashed_password: str) -> UserModel:
        model = UserModel(
            username=user.username,
            password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return model
