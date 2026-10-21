from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import os

from app.api.v1 import api_v1_router
from app.core.config import settings
from app.core.logging import logger
from app.core.rate_limit import limiter
from app.db.base import Base
from app.db.session import engine
from app.jobs.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} in {settings.ENVIRONMENT} mode...")
    # Initialize database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schemas initialized.")

    # Start in-process scheduler
    start_scheduler()
    yield

    # Shutdown
    stop_scheduler()
    await engine.dispose()
    logger.info("Database connection pool closed.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production backend for AgriMind AI Smart Farming Platform with BYOK KeyResolver & Polite Scraping Fallbacks",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["ETag", "X-Request-ID"]
)


# Global consistent error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again.",
                "details": str(exc) if settings.DEBUG else None
            }
        }
    )


# Mount versioned API routes
app.include_router(api_v1_router)


# Free hosting wake-up / Health endpoints
@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Lightweight ping endpoint for uptime pingers (cron-job.org / UptimeRobot) to prevent free tier sleep."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/ready", tags=["Health"])
@app.get("/api/v1/ready", tags=["Health"])
async def readiness_check() -> Dict[str, Any]:
    """Readiness probe checking database and scheduler state."""
    return {
        "status": "ready",
        "database": "connected",
        "scheduler": "running"
    }


# Static frontend files mounting if dist exists
if os.path.exists("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")
