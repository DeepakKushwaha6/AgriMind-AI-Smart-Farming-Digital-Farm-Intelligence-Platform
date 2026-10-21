from datetime import datetime, date, timezone
from sqlalchemy import String, Float, Integer, DateTime, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class MarketPrice(Base, TimestampMixin):
    __tablename__ = "market_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mandi_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), default="Jharkhand")
    commodity: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    variety: Mapped[str] = mapped_column(String(100), default="Common")

    min_price: Mapped[float] = mapped_column(Float, default=2290.0)
    max_price: Mapped[float] = mapped_column(Float, default=2410.0)
    modal_price: Mapped[float] = mapped_column(Float, default=2350.0)
    unit: Mapped[str] = mapped_column(String(20), default="Rs/Quintal")
    arrivals_ton: Mapped[float] = mapped_column(Float, default=145.0)
    distance_km: Mapped[float] = mapped_column(Float, default=12.0)
    transport_per_qtl: Mapped[float] = mapped_column(Float, default=28.0)
    handling_per_qtl: Mapped[float] = mapped_column(Float, default=18.0)
    weekly_change_pct: Mapped[str] = mapped_column(String(20), default="+3.2%")

    price_date: Mapped[date] = mapped_column(Date, default=date.today)
    source: Mapped[str] = mapped_column(String(100), default="CommodityOnline / Agmarknet Cleaned")
    source_type: Mapped[str] = mapped_column(String(30), default="scraped")
    source_url: Mapped[str] = mapped_column(String(255), default="https://www.commodityonline.com")
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False)
