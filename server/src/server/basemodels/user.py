from pydantic import BaseModel, ConfigDict


class UserSignupBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class UserDetailsBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    username: str
    first_name: str | None = None
    last_name: str | None = None
    disabled: bool = False


class UserLoginBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    password: str


class UserGetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    username: str
    first_name: str
    last_name: str
