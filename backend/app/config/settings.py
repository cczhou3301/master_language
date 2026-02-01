"""
Configuration with smooth switch: DEVELOPMENT <-> PRODUCTION.
Set APP_ENV=development | production (default: development).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator  # pyright: ignore[reportMissingImports]
from pydantic_settings import BaseSettings, SettingsConfigDict  # pyright: ignore[reportMissingImports]


EnvKind = Literal["development", "production"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- Environment ----
    APP_ENV: EnvKind = Field(
        default="development", description="development | production"
    )
    APP_NAME: str = "MasterLanguage"
    DEBUG: bool = Field(default=True, description="Verbose errors; off in production")

    # ---- Server ----
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = Field(default=1, description="Uvicorn workers; increase for HA")
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
        description="Comma-separated origins for CORS",
    )

    # ---- Database (MySQL) ----
    DATABASE_URL: str = Field(
        default="mysql+aiomysql://testUser:testPassword@localhost:3306/test_db?charset=utf8mb4",
        description="Async MySQL URL (mysql+aiomysql://...)",
    )
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # ---- Redis (sessions, rate limit, cache) ----
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    REDIS_RATE_LIMIT_DB: int = 1
    REDIS_SESSION_DB: int = 2

    # ---- Testing (skip auth when running tests) ----
    TESTING: bool = Field(
        default=False,
        description="If True, skip JWT validation; use TESTING_USER_ID when token missing (pytest, etc.).",
    )
    TESTING_USER_ID: int = Field(
        default=1, description="Default user_id when TESTING=True and no Bearer token."
    )

    # ---- Admin (avoids DAL in auth_deps; no cycle import) ----
    ADMIN_USER_IDS: str = Field(
        default="1",
        description="Comma-separated user_ids that are admin (e.g. 1 or 1,2,3). Used by get_current_admin_user_id.",
    )

    # ---- JWT / Auth ----
    JWT_SECRET_KEY: str = Field(
        default="dev-secret-change-in-production-min-32-chars",
        description="Must be long and random in production",
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = (
        15  # Short-lived; frontend refreshes with refresh token
    )
    JWT_REFRESH_EXPIRE_DAYS: int = (
        7  # Long-lived; stored in DB/Redis, used only for /refresh
    )

    # ---- Rate limiting (business rules from PRD) ----
    RATE_API_PER_SECOND: str = Field(
        default="5/1",
        description="Global API rate: N requests per second (e.g. 5/1 = 5 per 1 sec) per IP.",
    )
    RATE_ACTIVATION_PER_IP: str = "5/600"  # 5 per 10 min -> block IP 1h
    RATE_LOGIN_FAILED_PER_IP: str = "5/60"  # 5 per 1 min -> temp lock 15 min
    RATE_LOGIN_FAILED_PER_UID: str = "5/60"  # 5 per 1 min -> lock account
    RATE_VIDEO_PER_UID: str = "60/60"  # 60 per 1 min -> throttle
    RATE_VIDEO_PER_IP: str = "200/60"  # 200 per 1 min -> block IP 24h
    RATE_SMS_IP: str = "1/60"  # 1 per 60 sec
    RATE_GENERAL_UID: str = "1000/300"  # 1000 per 5 min -> 429

    # ---- Business ----
    MAX_DEVICES_PER_USER: int = 3
    LOGIN_FAILED_LOCK_MINUTES: int = 15
    ACTIVATION_BLOCK_IP_MINUTES: int = 60
    VIDEO_SCRAPE_BLOCK_IP_HOURS: int = 24

    @field_validator("APP_ENV", mode="before")
    @classmethod
    def normalize_app_env(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().lower()
            if v in ("dev", "develop"):
                return "development"
            if v in ("prod", "produce"):
                return "production"
        return v or "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    def admin_user_ids_list(self) -> list[int]:
        """Parse ADMIN_USER_IDS to list of int (e.g. '1,2,3' -> [1, 2, 3])."""
        result: list[int] = []
        for part in (self.ADMIN_USER_IDS or "").split(","):
            part = part.strip()
            if part and part.isdigit():
                result.append(int(part))
        return result


@lru_cache
def get_settings() -> Settings:
    return Settings()
