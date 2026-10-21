from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "AgriMind AI Backend"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # CORS
    FRONTEND_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://agrimind.vercel.app"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",") if origin.strip()]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./agrimind.db"

    # Security
    JWT_SECRET_KEY: str = "super-secret-jwt-key-for-agrimind-change-in-production-12345"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    APP_ENCRYPTION_KEY: str = "P4_4g5g2sYqP3d0XpI1W8V7qN6mK3zJ8bF5d2sA0eC="

    # Default Admin
    ADMIN_EMAIL: str = "deepak.kumar.agri@jarga-farms.in"
    ADMIN_PASSWORD: str = "AgriMindAdmin@2026!"
    ADMIN_NAME: str = "Deepak Kumar"

    # External Provider Keys
    OPENROUTER_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    DATA_GOV_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = "AIzaSyBlhF1v3r9aXsdZN4byYfNjRqjYokmzlHw"
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


settings = Settings()
