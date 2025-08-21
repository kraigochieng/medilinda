from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None
    
class UserInDB(User):
    hashed_password: str

class UserSignupBaseModel(BaseModel):
    username: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class UserDetailsBaseModel(BaseModel):
    id: str | None = None
    username: str
    first_name: str | None = None
    last_name: str | None = None


class UserLoginBaseModel(BaseModel):
    username: str
    password: str


class UserGetResponse(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str
