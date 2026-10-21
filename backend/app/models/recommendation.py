from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), default="Plot A — North Lowland")
    category: Mapped[str] = mapped_column(String(50), default="Irrigation & Drainage")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[str] = mapped_column(String(50), default="92% (Very High)")
    risk_and_limitations: Mapped[str] = mapped_column(Text, nullable=False)
    alternative: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="Active")  # Active, Completed, Dismissed
    outcome_recorded: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    feedback_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    model_version: Mapped[str] = mapped_column(String(100), default="DecisionEngine-v1.0+Llama-3.3-70B:free")

    user: Mapped["User"] = relationship("User", back_populates="recommendations")
