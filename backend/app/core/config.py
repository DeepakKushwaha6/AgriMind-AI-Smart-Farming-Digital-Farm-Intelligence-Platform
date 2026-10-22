import os
import secrets
from typing import List
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet


KNOWN_INSECURE_SECRETS = {
    "super-secret-jwt-key-for-agrimind-change-in-production-12345",
    "change-this-in-production-super-secret-key-at-least-32-chars",
    "agrimind-secret-key-production-2026",
    "P4_4g5g2sYqP3d0XpI1W8V7qN6mK3zJ8bF5d2sA0eC=",
    "AgriMindAdmin@2026!",
    "admin123",
    "password",
    "secret",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "AgriMind AI Backend"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # CORS
    FRONTEND_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",") if origin.strip()]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./agrimind.db"

    # Security
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    APP_ENCRYPTION_KEY: str = ""

    # Default Admin
    ADMIN_EMAIL: str = "deepak.kumar.agri@jarga-farms.in"
    ADMIN_PASSWORD: str = ""
    ADMIN_NAME: str = "Deepak Kumar"

    # External Provider Keys
    OPENROUTER_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    DATA_GOV_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    COPENICUS_CLIENT_ID: str = ""
    COPENICUS_CLIENT_SECRET: str = ""

    # Scraper settings
    SCRAPER_RATE_LIMIT_SECONDS: float = 3.0
    SCRAPER_USER_AGENT: str = (
        "AgriMindAI-Bot/1.0 (+https://agrimind.org/bot; polite agricultural telemetry)"
    )
    SCRAPER_CACHE_TTL_HOURS: int = 2
    WEATHER_CACHE_TTL_MINUTES: int = 60
    MARKET_CACHE_TTL_HOURS: int = 6

    @model_validator(mode="after")
    def validate_production_and_keys(self) -> "Settings":
        is_prod = self.ENVIRONMENT.lower() == "production"

        # Production security assertion
        if is_prod:
            if not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY in KNOWN_INSECURE_SECRETS or len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("FATAL: JWT_SECRET_KEY must be set to a secure, unique string (min 32 chars) in production.")
            if not self.APP_ENCRYPTION_KEY or self.APP_ENCRYPTION_KEY in KNOWN_INSECURE_SECRETS:
                raise ValueError("FATAL: APP_ENCRYPTION_KEY must be set to a secure, unique Fernet key in production.")
            try:
                Fernet(self.APP_ENCRYPTION_KEY.encode())
            except Exception as e:
                raise ValueError(f"FATAL: APP_ENCRYPTION_KEY is not a valid 32-byte urlsafe-base64 Fernet key: {e}")
            if not self.ADMIN_PASSWORD or self.ADMIN_PASSWORD in KNOWN_INSECURE_SECRETS or len(self.ADMIN_PASSWORD) < 12:
                raise ValueError("FATAL: ADMIN_PASSWORD must be configured with a strong non-default secret (min 12 chars) in production.")
        else:
            # Development fallbacks
            if not self.JWT_SECRET_KEY:
                self.JWT_SECRET_KEY = secrets.token_hex(32)
            if not self.APP_ENCRYPTION_KEY:
                self.APP_ENCRYPTION_KEY = Fernet.generate_key().decode()
            else:
                try:
                    Fernet(self.APP_ENCRYPTION_KEY.encode())
                except Exception as e:
                    raise ValueError(f"Invalid APP_ENCRYPTION_KEY: must be a 32-byte urlsafe-base64 Fernet key: {e}")
            if not self.ADMIN_PASSWORD:
                self.ADMIN_PASSWORD = "DevAdminTempPassword2026!#"

        return self


settings = Settings()
