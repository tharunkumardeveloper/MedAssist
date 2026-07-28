import secrets
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = secrets.token_hex(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day

    database_url: str = "sqlite:///./medassist.db"

    cors_origins: str = "http://localhost:8501,http://127.0.0.1:8501,http://localhost:5173,http://127.0.0.1:5173"

    login_rate_limit_attempts: int = 10
    login_rate_limit_window_seconds: int = 60

    # If both are set and no admin user exists yet, one is created on startup.
    bootstrap_admin_email: Optional[str] = None
    bootstrap_admin_password: Optional[str] = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
