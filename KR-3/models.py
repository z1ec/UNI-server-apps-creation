from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)


class User(UserBase):
    password: str = Field(..., min_length=1, max_length=128)


class UserInDB(UserBase):
    hashed_password: str


class TokenRequest(User):
    pass
