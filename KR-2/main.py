from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from itsdangerous import BadSignature, Signer
from pydantic import ValidationError

from models import CommonHeaders, LoginData, UserCreate


app = FastAPI(title="KR-2")

SESSION_COOKIE_NAME = "session_token"
SESSION_TTL_SECONDS = 300
SESSION_REFRESH_AFTER_SECONDS = 180
SECRET_KEY = "kr-2-secret-key"

signer = Signer(SECRET_KEY)

PRODUCTS = [
    {
        "product_id": 123,
        "name": "Smartphone",
        "category": "Electronics",
        "price": 599.99,
    },
    {
        "product_id": 456,
        "name": "Phone Case",
        "category": "Accessories",
        "price": 19.99,
    },
    {
        "product_id": 789,
        "name": "Iphone",
        "category": "Electronics",
        "price": 1299.99,
    },
    {
        "product_id": 101,
        "name": "Headphones",
        "category": "Accessories",
        "price": 99.99,
    },
    {
        "product_id": 202,
        "name": "Smartwatch",
        "category": "Electronics",
        "price": 299.99,
    },
]

FAKE_USER = {
    "username": "user123",
    "password": "password123",
    "name": "Demo User",
    "role": "student",
    "email": "user123@example.com",
}
ACTIVE_SESSIONS: dict[str, dict[str, Any]] = {}


class SessionError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED) -> None:
        self.message = message
        self.status_code = status_code


@app.exception_handler(SessionError)
async def handle_session_error(_: Request, exc: SessionError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})


def now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def build_session_token(user_id: str, timestamp: int) -> str:
    payload = f"{user_id}.{timestamp}"
    return signer.sign(payload.encode()).decode()


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,
        max_age=SESSION_TTL_SECONDS,
    )


async def parse_login_data(request: Request) -> LoginData:
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        payload = await request.json()
    elif "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        payload = dict(form)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported content type",
        )

    try:
        return LoginData.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.errors(),
        ) from exc


def get_common_headers(
    user_agent: str | None = Header(default=None),
    accept_language: str | None = Header(default=None),
) -> CommonHeaders:
    if not user_agent or not accept_language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required headers",
        )

    try:
        return CommonHeaders.model_validate(
            {
                "User-Agent": user_agent,
                "Accept-Language": accept_language,
            }
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.errors(),
        ) from exc


def validate_session_token(token: str) -> tuple[str, int]:
    try:
        unsigned_value = signer.unsign(token).decode()
    except BadSignature as exc:
        raise SessionError("Invalid session") from exc

    parts = unsigned_value.split(".")
    if len(parts) != 2:
        raise SessionError("Invalid session")

    user_id, timestamp_raw = parts

    try:
        UUID(user_id)
        timestamp = int(timestamp_raw)
    except ValueError as exc:
        raise SessionError("Invalid session") from exc

    return user_id, timestamp


def authenticate_session(
    response: Response,
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> dict[str, Any]:
    if not session_token:
        raise SessionError("Unauthorized")

    user_id, last_activity = validate_session_token(session_token)
    session = ACTIVE_SESSIONS.get(user_id)

    if not session or session["token"] != session_token:
        raise SessionError("Unauthorized")

    elapsed = now_ts() - last_activity
    if elapsed > SESSION_TTL_SECONDS:
        ACTIVE_SESSIONS.pop(user_id, None)
        raise SessionError("Session expired")

    refreshed = False
    if elapsed >= SESSION_REFRESH_AFTER_SECONDS:
        new_timestamp = now_ts()
        new_token = build_session_token(user_id, new_timestamp)
        ACTIVE_SESSIONS[user_id]["token"] = new_token
        ACTIVE_SESSIONS[user_id]["last_activity"] = new_timestamp
        set_session_cookie(response, new_token)
        refreshed = True

    return {
        "user_id": user_id,
        "username": session["username"],
        "name": session["name"],
        "role": session["role"],
        "email": session["email"],
        "last_activity": ACTIVE_SESSIONS[user_id]["last_activity"],
        "session_refreshed": refreshed,
    }


@app.post("/create_user")
async def create_user(user: UserCreate) -> UserCreate:
    return user


@app.get("/products/search")
async def search_products(
    keyword: str,
    category: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    filtered_products = [
        product
        for product in PRODUCTS
        if keyword.lower() in product["name"].lower()
        and (category is None or product["category"].lower() == category.lower())
    ]
    return filtered_products[:limit]


@app.get("/product/{product_id}")
async def get_product(product_id: int) -> dict[str, Any]:
    for product in PRODUCTS:
        if product["product_id"] == product_id:
            return product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found",
    )


@app.post("/login")
async def login(request: Request, response: Response, credentials: LoginData = Depends(parse_login_data)) -> dict[str, str]:
    if (
        credentials.username != FAKE_USER["username"]
        or credentials.password != FAKE_USER["password"]
    ):
        raise SessionError("Unauthorized")

    user_id = str(uuid4())
    timestamp = now_ts()
    token = build_session_token(user_id, timestamp)

    ACTIVE_SESSIONS[user_id] = {
        "token": token,
        "last_activity": timestamp,
        "username": FAKE_USER["username"],
        "name": FAKE_USER["name"],
        "role": FAKE_USER["role"],
        "email": FAKE_USER["email"],
    }
    set_session_cookie(response, token)

    return {
        "message": "Logged in successfully",
        "session_token": token,
    }


@app.get("/user")
async def get_user_profile(
    response: Response,
    session: dict[str, Any] = Depends(authenticate_session),
) -> dict[str, Any]:
    return {
        "user_id": session["user_id"],
        "username": session["username"],
        "name": session["name"],
        "role": session["role"],
        "email": session["email"],
    }


@app.get("/profile")
async def get_profile(
    response: Response,
    session: dict[str, Any] = Depends(authenticate_session),
) -> dict[str, Any]:
    return {
        "message": "Profile access granted",
        "profile": {
            "user_id": session["user_id"],
            "username": session["username"],
            "name": session["name"],
            "role": session["role"],
            "email": session["email"],
        },
        "last_activity": session["last_activity"],
        "session_refreshed": session["session_refreshed"],
    }


@app.get("/headers")
async def read_headers(headers: CommonHeaders = Depends(get_common_headers)) -> dict[str, str]:
    return headers.as_response_dict()


@app.get("/info")
async def read_info(
    response: Response,
    headers: CommonHeaders = Depends(get_common_headers),
) -> dict[str, Any]:
    response.headers["X-Server-Time"] = datetime.now().isoformat(timespec="seconds")
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": headers.as_response_dict(),
    }
