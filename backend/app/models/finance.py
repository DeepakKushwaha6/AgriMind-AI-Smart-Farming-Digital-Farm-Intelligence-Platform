from datetime import date
from typing import Optional
from sqlalchemy import String, Float, Integer, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Expense(Base, TimestampMixin):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    date: Mapped[date] = mapped_column(Date, default=date.today)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # Seeds, Fertilizer, Labour, Machinery
    item_description: Mapped[str] = mapped_column(String(200), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), default="Plot A")
    planned_amount: Mapped[float] = mapped_column(Float, default=0.0)
    actual_amount: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="finances_expenses")


class Revenue(Base, TimestampMixin):
    __tablename__ = "revenues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    date: Mapped[date] = mapped_column(Date, default=date.today)
    category: Mapped[str] = mapped_column(String(50), default="Sales")  # Harvest Sale, Subsidies
    item_description: Mapped[str] = mapped_column(String(200), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), default="Plot A")
    planned_amount: Mapped[float] = mapped_column(Float, default=0.0)
    actual_amount: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_qtl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rate_per_qtl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="finances_revenues")


class YieldRecord(Base, TimestampMixin):
    __tablename__ = "yield_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    variety: Mapped[str] = mapped_column(String(100), nullable=False)
    harvest_date: Mapped[date] = mapped_column(Date, default=date.today)
    yield_quintals: Mapped[float] = mapped_column(Float, nullable=False)
    moisture_percentage: Mapped[float] = mapped_column(Float, default=13.5)
    quality_grade: Mapped[str] = mapped_column(String(20), default="Grade A")
