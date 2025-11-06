from sqlalchemy.orm import Session
from server.models.user import UserModel
from sqlalchemy import select
from server.exceptions import ResourceNotFoundError


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> UserModel:
        stmt = select(UserModel).where(UserModel.username == username)
        
        model = self.db.scalar(stmt)

        if not model:
            raise ResourceNotFoundError(f"User with username {username} not found")

        return model
