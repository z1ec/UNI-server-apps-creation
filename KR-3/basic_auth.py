import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from models import UserBase, UserInDB


security = HTTPBasic()


def unauthorized(detail: str = "Unauthorized") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Basic"},
    )


def verify_basic_credentials(
    credentials: HTTPBasicCredentials = Depends(security),
    expected_username: str = "admin",
    expected_password: str = "qwerty",
) -> str:
    is_valid = secrets.compare_digest(credentials.username, expected_username) and secrets.compare_digest(
        credentials.password, expected_password
    )
    if not is_valid:
        raise unauthorized("Incorrect username or password")
    return credentials.username


def find_user_by_username(username: str, users_db: dict[str, UserInDB]) -> UserInDB | None:
    for stored_username, user in users_db.items():
        if secrets.compare_digest(stored_username, username):
            return user
    return None


def welcome_user(user: UserBase) -> dict[str, str]:
    return {"message": f"Welcome, {user.username}!"}
