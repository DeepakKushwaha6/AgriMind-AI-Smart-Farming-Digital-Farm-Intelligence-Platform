from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decrypt_api_key
from app.models.user import UserApiKey, ApiKeyCategory, ApiKeyStatus
from app.core.config import settings
from app.core.logging import logger


class KeyResolver:
    """
    Resolves the external data provider chain in strict priority order:
    1) User's own API key(s) in priority order
    2) Server's shared key (if configured and quota allows)
    3) Free keyless API (Open-Meteo, SoilGrids, Nominatim, etc.)
    4) Web Scraper fallback connector
    5) Last cached value, marked stale
    """

    @staticmethod
    async def get_user_key(
        db: AsyncSession,
        user_id: int,
        category: ApiKeyCategory
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves the highest-priority active user key for a category.
        Decrypted key is returned ONLY for server-side connector execution and never exposed to client or logs.
        """
        stmt = (
            select(UserApiKey)
            .where(
                UserApiKey.user_id == user_id,
                UserApiKey.category == category,
                UserApiKey.status.in_([ApiKeyStatus.ACTIVE, ApiKeyStatus.UNTESTED])
            )
            .order_by(UserApiKey.priority.asc(), UserApiKey.id.asc())
        )
        res = await db.execute(stmt)
        key_record = res.scalars().first()

        if not key_record:
            return None

        plain_key = decrypt_api_key(key_record.encrypted_key)
        if not plain_key:
            return None

        return {
            "id": key_record.id,
            "provider_name": key_record.provider_name,
            "category": key_record.category.value,
            "api_key": plain_key,
            "priority": key_record.priority,
            "status": key_record.status.value
        }

    @staticmethod
    def get_shared_server_key(category: ApiKeyCategory) -> Optional[str]:
        """Returns the shared server environment key for a category if available."""
        if category == ApiKeyCategory.WEATHER:
            return None  # Defaults to Open-Meteo free API
        if category == ApiKeyCategory.MANDI:
            return settings.DATA_GOV_API_KEY or None
        if category == ApiKeyCategory.MAPS:
            return settings.GOOGLE_MAPS_API_KEY or None
        if category == ApiKeyCategory.AI:
            return settings.OPENROUTER_API_KEY or settings.GEMINI_API_KEY or None
        return None
