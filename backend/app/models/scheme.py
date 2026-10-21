from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class SchemeRecord(Base, TimestampMixin):
    __tablename__ = "scheme_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    benefit_summary: Mapped[str] = mapped_column(Text, nullable=False)
    documents_required: Mapped[str] = mapped_column(Text, nullable=False)
    official_url: Mapped[str] = mapped_column(String(255), nullable=False)
    status_tag: Mapped[str] = mapped_column(String(100), default="Enrolled")
    last_verified: Mapped[str] = mapped_column(String(50), default="October 2026")
    last_checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
