import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.mode = os.getenv("MODE", "DEV").upper()
        self.docs_user = os.getenv("DOCS_USER", "docs")
        self.docs_password = os.getenv("DOCS_PASSWORD", "docs123")
        self.jwt_secret = os.getenv("JWT_SECRET", "kr-3-secret")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
        self.jwt_demo_username = os.getenv("JWT_DEMO_USERNAME", "john_doe")
        self.jwt_demo_password = os.getenv("JWT_DEMO_PASSWORD", "securepassword123")
        if self.mode not in {"DEV", "PROD"}:
            raise RuntimeError("MODE must be DEV or PROD")


settings = Settings()
