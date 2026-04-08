from fastapi import Depends, FastAPI, HTTPException, Request, status

from basic_auth import find_user_by_username
from jwt_auth import create_access_token, get_current_subject
from models import User, UserInDB
from passwords import hash_password, verify_password
from rate_limit import RateLimiter


app = FastAPI(title="KR-3 Task 6.5")

fake_users_db: dict[str, UserInDB] = {}
rate_limiter = RateLimiter()


def client_key(request: Request, endpoint: str) -> str:
    host = request.client.host if request.client else "anonymous"
    return f"{endpoint}:{host}"


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: User, request: Request) -> dict[str, str]:
    rate_limiter.hit(client_key(request, "register"), limit=1, window_seconds=60)
    if find_user_by_username(user.username, fake_users_db) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    fake_users_db[user.username] = UserInDB(
        username=user.username,
        hashed_password=hash_password(user.password),
    )
    return {"message": "New user created"}


@app.post("/login")
def login(user: User, request: Request) -> dict[str, str]:
    rate_limiter.hit(client_key(request, "login"), limit=5, window_seconds=60)
    stored_user = find_user_by_username(user.username, fake_users_db)
    if stored_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not verify_password(user.password, stored_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
        )
    return {
        "access_token": create_access_token(stored_user.username),
        "token_type": "bearer",
    }


@app.get("/protected_resource")
def protected_resource(subject: str = Depends(get_current_subject)) -> dict[str, str]:
    return {"message": "Access granted", "username": subject}
