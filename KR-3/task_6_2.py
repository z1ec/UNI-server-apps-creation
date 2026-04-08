from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasicCredentials

from basic_auth import find_user_by_username, security, unauthorized, welcome_user
from models import User, UserInDB
from passwords import hash_password, verify_password


app = FastAPI(title="KR-3 Task 6.2")

fake_users_db: dict[str, UserInDB] = {}


def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    user = find_user_by_username(credentials.username, fake_users_db)
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise unauthorized("Incorrect username or password")
    return user


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: User) -> dict[str, str]:
    if find_user_by_username(user.username, fake_users_db) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    fake_users_db[user.username] = UserInDB(
        username=user.username,
        hashed_password=hash_password(user.password),
    )
    return {"message": "User added successfully"}


@app.get("/login")
def login(user: UserInDB = Depends(auth_user)) -> dict[str, str]:
    return welcome_user(user)
