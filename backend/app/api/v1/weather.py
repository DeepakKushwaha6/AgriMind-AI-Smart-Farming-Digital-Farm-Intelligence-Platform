from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.connectors.weather_connector import WeatherConnector
from app.db.session import get_db
from app.models.user import User, ApiKeyCategory
from app.services.key_resolver import KeyResolver

router = APIRouter(prefix="/weather", tags=["Weather"])
weather_connector = WeatherConnector()


@router.get("", response_model=Dict[str, Any])
async def get_weather_forecast(
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    location_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns real-time agro-weather, 7-day forecast, ET0, rain trend, and spray windows."""
    query_lat = lat if lat is not None else current_user.lat
    query_lon = lon if lon is not None else current_user.lon
    loc = location_name or f"{current_user.village}, {current_user.district}"

    user_weather_key = await KeyResolver.get_user_key(db, current_user.id, ApiKeyCategory.WEATHER)
    return await weather_connector.get_weather(
        lat=query_lat,
        lon=query_lon,
        location_name=loc,
        user_key_info=user_weather_key
    )
