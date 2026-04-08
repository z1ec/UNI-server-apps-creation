import secrets

from fastapi import Depends, FastAPI, HTTPException, status

from config import settings
from jwt_auth import create_access_token, get_current_subject
from models import TokenRequest


app = FastAPI(title="KR-3 Task 6.4")


def authenticate_user(username: str, password: str) -> bool:
    return secrets.compare_digest(username, settings.jwt_demo_username) and secrets.compare_digest(
        password, settings.jwt_demo_password
    )


@app.post("/login")
def login(payload: TokenRequest) -> dict[str, str]:
    if not authenticate_user(payload.username, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return {"access_token": create_access_token(payload.username)}


@app.get("/protected_resource")
def protected_resource(subject: str = Depends(get_current_subject)) -> dict[str, str]:
    return {"message": f"Access granted for {subject}"}
