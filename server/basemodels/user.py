from pydantic import BaseModel


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
    disabled: bool = False


class UserLoginBaseModel(BaseModel):
    username: str
    password: str


class UserGetResponse(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str
