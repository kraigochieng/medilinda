from sqlalchemy.orm import Session
from server.models.user import UserModel
from sqlalchemy import select


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.username == username)

        return self.db.scalar(stmt)
