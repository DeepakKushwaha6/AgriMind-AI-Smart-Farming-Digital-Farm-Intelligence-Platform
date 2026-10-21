from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Text, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class ScrapeTarget(Base, TimestampMixin):
    """Registered scraping targets with selectors and rate limits."""
    __tablename__ = "scrape_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # weather, mandi, schemes, news
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_url: Mapped[str] = mapped_column(String(255), nullable=False)
    selector_config_json: Mapped[str] = mapped_column(Text, nullable=False)
    rate_limit_seconds: Mapped[float] = mapped_column(Float, default=3.0)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_etag: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_modified_header: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class ScrapeRun(Base, TimestampMixin):
    """Audit log of every automated scrape execution."""
    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    target_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)  # SUCCESS, 304_NOT_MODIFIED, PARSE_ERROR, RATE_LIMITED, BLOCKED
    http_status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    items_extracted_count: Mapped[int] = mapped_column(Integer, default=0)
    error_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
