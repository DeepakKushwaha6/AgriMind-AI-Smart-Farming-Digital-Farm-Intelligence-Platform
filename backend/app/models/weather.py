from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class WeatherSnapshot(Base, TimestampMixin):
    __tablename__ = "weather_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lat_round: Mapped[float] = mapped_column(Float, index=True, nullable=False)
    lon_round: Mapped[float] = mapped_column(Float, index=True, nullable=False)
    location_name: Mapped[str] = mapped_column(String(100), default="Jarga, Hazaribagh")

    temp_c: Mapped[int] = mapped_column(Integer, default=28)
    humidity: Mapped[int] = mapped_column(Integer, default=92)
    condition: Mapped[str] = mapped_column(String(50), default="Light Rain")
    wind_kph: Mapped[float] = mapped_column(Float, default=14.2)
    rain_7d_mm: Mapped[float] = mapped_column(Float, default=42.0)
    rain_trend: Mapped[str] = mapped_column(String(50), default="Above Normal")
    et0_mm_day: Mapped[float] = mapped_column(Float, default=4.1)
    soil_moisture_pct: Mapped[int] = mapped_column(Integer, default=26)
    soil_temp_c: Mapped[float] = mapped_column(Float, default=26.4)
    daily_forecast_json: Mapped[str] = mapped_column(Text, default="[]")

    # Provenance
    source: Mapped[str] = mapped_column(String(100), default="Open-Meteo Agro API")
    source_type: Mapped[str] = mapped_column(String(30), default="free_api")  # user_api, shared_api, free_api, scraped, cache
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False)
    fallback_reason: Mapped[str] = mapped_column(String(100), default="None")
