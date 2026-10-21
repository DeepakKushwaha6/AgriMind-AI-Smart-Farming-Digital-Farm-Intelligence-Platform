from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class DataSource(Base, TimestampMixin):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # weather, market, geocoding, soil, satellite, ai
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    active_source: Mapped[str] = mapped_column(String(100), nullable=False)
    fallback_chain: Mapped[str] = mapped_column(Text, default="[]")
    last_successful_fetch: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    freshness_label: Mapped[str] = mapped_column(String(50), default="Fresh (< 15m)")
    latency_ms: Mapped[int] = mapped_column(Integer, default=320)
    error_rate_pct: Mapped[float] = mapped_column(Float, default=0.0)
    users_on_byok_count: Mapped[int] = mapped_column(Integer, default=0)
    is_healthy: Mapped[bool] = mapped_column(Boolean, default=True)


class ApiProviderHealth(Base, TimestampMixin):
    __tablename__ = "api_provider_health"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="HEALTHY")  # HEALTHY, DEGRADED, DOWN, COOLDOWN
    last_ping_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class SyncLog(Base, TimestampMixin):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp_str: Mapped[str] = mapped_column(String(50), nullable=False)
    stage: Mapped[str] = mapped_column(String(100), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PASS")  # PASS, CACHED, FAIL


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(30), default="weather")  # weather, irrigation, market, task
    icon: Mapped[str] = mapped_column(String(10), default="🔔")
    color: Mapped[str] = mapped_column(String(20), default="emerald")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="notifications")


class AiModelStat(Base, TimestampMixin):
    __tablename__ = "ai_model_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    short_name: Mapped[str] = mapped_column(String(50), nullable=False)
    specialty: Mapped[str] = mapped_column(String(30), default="fast")  # fast, reasoning, vision
    context_tokens: Mapped[str] = mapped_column(String(20), default="128K")
    rpm_limit: Mapped[int] = mapped_column(Integer, default=20)
    heat_pct: Mapped[int] = mapped_column(Integer, default=10)
    latency_ms: Mapped[int] = mapped_column(Integer, default=650)
    status: Mapped[str] = mapped_column(String(30), default="STANDBY")  # ACTIVE, STANDBY, COOLING_DOWN
    calls_made: Mapped[int] = mapped_column(Integer, default=0)
    cooldown_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
