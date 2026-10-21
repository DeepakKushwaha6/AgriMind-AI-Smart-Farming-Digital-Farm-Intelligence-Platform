from datetime import date
from typing import Optional, List
from sqlalchemy import String, Float, Integer, ForeignKey, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Farm(Base, TimestampMixin):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    total_area_acres: Mapped[float] = mapped_column(Float, default=2.0)
    original_unit_value: Mapped[float] = mapped_column(Float, default=64.0)
    original_unit_name: Mapped[str] = mapped_column(String(50), default="Katha (Jharkhand 32 Katha/Acre)")
    tenure: Mapped[str] = mapped_column(String(50), default="Owned")
    location: Mapped[str] = mapped_column(String(200), default="Jarga, Hazaribagh, Jharkhand")
    lat: Mapped[float] = mapped_column(Float, default=24.002)
    lon: Mapped[float] = mapped_column(Float, default=85.361)

    owner: Mapped["User"] = relationship("User", back_populates="farms")
    fields: Mapped[List["Field"]] = relationship("Field", back_populates="farm", cascade="all, delete-orphan")


class Field(Base, TimestampMixin):
    __tablename__ = "fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), default="FLD-01")
    area_acres: Mapped[float] = mapped_column(Float, nullable=False)
    area_hectares: Mapped[float] = mapped_column(Float, default=0.0)
    soil_type: Mapped[str] = mapped_column(String(100), default="Clay Loam (pH 6.1)")
    water_source: Mapped[str] = mapped_column(String(100), default="Solar Borewell + Check Dam")
    geojson_boundary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lat: Mapped[float] = mapped_column(Float, default=24.002)
    lon: Mapped[float] = mapped_column(Float, default=85.361)

    farm: Mapped["Farm"] = relationship("Farm", back_populates="fields")
    crop_cycles: Mapped[List["CropCycle"]] = relationship("CropCycle", back_populates="field", cascade="all, delete-orphan")


class CropCycle(Base, TimestampMixin):
    __tablename__ = "crop_cycles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    field_id: Mapped[int] = mapped_column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), index=True, nullable=False)
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    variety: Mapped[str] = mapped_column(String(100), nullable=False)
    season: Mapped[str] = mapped_column(String(50), default="Kharif 2025")
    sowing_date: Mapped[date] = mapped_column(Date, default=date.today)
    expected_harvest_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    stage: Mapped[str] = mapped_column(String(100), default="Active Tillering")
    status: Mapped[str] = mapped_column(String(50), default="Active")  # Active, Harvested, Planned
    expected_yield_qtl: Mapped[float] = mapped_column(Float, default=22.0)
    actual_yield_qtl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    expected_profit_inr: Mapped[float] = mapped_column(Float, default=35000.0)
    actual_profit_inr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    field: Mapped["Field"] = relationship("Field", back_populates="crop_cycles")
