from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator


EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
ACCEPT_LANGUAGE_REGEX = re.compile(
    r"^[a-zA-Z]{2,3}(?:-[a-zA-Z]{2})?(?:,[a-zA-Z]{2,3}(?:-[a-zA-Z]{2})?(?:;q=(?:0(?:\.\d+)?|1(?:\.0+)?))?)*$"
)


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    age: int | None = Field(default=None, gt=0)
    is_subscribed: bool | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not EMAIL_REGEX.fullmatch(value):
            raise ValueError("Invalid email format")
        return value


class LoginData(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=128)


class CommonHeaders(BaseModel):
    user_agent: str = Field(..., min_length=1, alias="User-Agent")
    accept_language: str = Field(..., min_length=1, alias="Accept-Language")

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, value: str) -> str:
        if not ACCEPT_LANGUAGE_REGEX.fullmatch(value):
            raise ValueError("Invalid Accept-Language format")
        return value

    def as_response_dict(self) -> dict[str, str]:
        return {
            "User-Agent": self.user_agent,
            "Accept-Language": self.accept_language,
        }
