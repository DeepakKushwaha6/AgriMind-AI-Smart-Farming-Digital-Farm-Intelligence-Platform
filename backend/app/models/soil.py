from datetime import date
from typing import Optional
from sqlalchemy import String, Float, Integer, ForeignKey, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class SoilRecord(Base, TimestampMixin):
    __tablename__ = "soil_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), default="Plot A — North Lowland")
    sample_id: Mapped[str] = mapped_column(String(100), default="SHC-JH-HZB-2025-0891")
    sample_date: Mapped[date] = mapped_column(Date, default=date.today)
    source_type: Mapped[str] = mapped_column(String(50), default="Lab-Measured (Soil Health Card)")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)

    # Core Parameters
    ph: Mapped[float] = mapped_column(Float, default=6.1)
    ec: Mapped[float] = mapped_column(Float, default=0.28)
    organic_carbon_pct: Mapped[float] = mapped_column(Float, default=0.58)
    nitrogen_kg_ha: Mapped[float] = mapped_column(Float, default=218.0)
    phosphorus_kg_ha: Mapped[float] = mapped_column(Float, default=19.4)
    potassium_kg_ha: Mapped[float] = mapped_column(Float, default=184.0)

    # Micronutrients
    zinc_ppm: Mapped[float] = mapped_column(Float, default=0.52)
    boron_ppm: Mapped[float] = mapped_column(Float, default=0.41)
    sulphur_ppm: Mapped[float] = mapped_column(Float, default=11.2)
    iron_ppm: Mapped[Optional[float]] = mapped_column(Float, default=4.5)

    user: Mapped["User"] = relationship("User", back_populates="soil_records")
