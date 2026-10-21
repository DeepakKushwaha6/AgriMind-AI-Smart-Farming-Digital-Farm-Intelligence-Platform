from datetime import date
from typing import Optional
from sqlalchemy import String, Boolean, Integer, ForeignKey, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), default="Plot A — North Lowland")
    category: Mapped[str] = mapped_column(String(50), default="Agronomy")  # Nutrient, Scouting, Irrigation, Harvest
    priority: Mapped[str] = mapped_column(String(20), default="Medium")     # High, Medium, Low
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    has_reminder: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User", back_populates="tasks")
