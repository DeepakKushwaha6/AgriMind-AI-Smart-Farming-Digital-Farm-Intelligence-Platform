from typing import Optional
from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Machinery(Base, TimestampMixin):
    __tablename__ = "machinery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    mode: Mapped[str] = mapped_column(String(50), default="Owned")  # Owned, Rented, CHC
    cost_per_hr: Mapped[float] = mapped_column(Float, default=280.0)
    custom_hire_rate_hr: Mapped[float] = mapped_column(Float, default=650.0)
    hours_used_season: Mapped[float] = mapped_column(Float, default=0.0)
    fuel_litres_hr: Mapped[float] = mapped_column(Float, default=1.4)
    status: Mapped[str] = mapped_column(String(50), default="Operational")
    next_service: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="machinery")
