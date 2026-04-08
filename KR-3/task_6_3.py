import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasicCredentials

from basic_auth import security
from config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="KR-3 Task 6.3",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    @app.get("/")
    def root() -> dict[str, str]:
        return {"mode": settings.mode}

    if settings.mode == "DEV":

        @app.get("/docs", include_in_schema=False)
        def custom_swagger(_: str = Depends(docs_auth)):
            return get_swagger_ui_html(
                openapi_url="/openapi.json",
                title=f"{app.title} - Docs",
            )

        @app.get("/openapi.json", include_in_schema=False)
        def openapi(_: str = Depends(docs_auth)) -> JSONResponse:
            return JSONResponse(app.openapi())

    return app


def docs_auth(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    is_valid = secrets.compare_digest(credentials.username, settings.docs_user) and secrets.compare_digest(
        credentials.password, settings.docs_password
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


app = create_app()
