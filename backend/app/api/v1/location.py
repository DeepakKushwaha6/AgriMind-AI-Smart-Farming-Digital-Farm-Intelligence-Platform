from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.connectors.geocoding_connector import GeocodingConnector
from app.db.session import get_db
from app.models.user import User, ApiKeyCategory
from app.services.key_resolver import KeyResolver

router = APIRouter(prefix="/location", tags=["Location & Geocoding"])
geocoding_connector = GeocodingConnector()


@router.get("/geocode", response_model=List[Dict[str, Any]])
async def search_location(
    q: str = Query(..., min_length=2),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Searches locations via Google Maps Geocoding API with Nominatim OpenStreetMap fallback."""
    user_maps_key = await KeyResolver.get_user_key(db, current_user.id, ApiKeyCategory.MAPS)
    return await geocoding_connector.geocode(query=q, user_key_info=user_maps_key)
