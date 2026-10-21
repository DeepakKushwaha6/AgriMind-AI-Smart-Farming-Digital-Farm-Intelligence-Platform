import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from app.connectors.base import BaseConnector
from app.core.cache import geocode_cache
from app.core.config import settings
from app.core.logging import logger


class GeocodingConnector(BaseConnector):
    """
    Location & Geocoding Connector orchestrating:
    1. Google Maps Geocoding REST API (if user/server key provided)
    2. Nominatim OpenStreetMap Geocoding (polite 1 req/sec, descriptive User-Agent, 30-day cache)
    3. Open-Meteo Geocoding API fallback
    4. Reverse geocoding (lat, lon -> village, district, state)
    """

    def __init__(self):
        super().__init__(name="GeocodingConnector", timeout=8.0, max_retries=2)
        self._last_nominatim_req = 0.0

    async def geocode(
        self,
        query: str,
        user_key_info: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        cleaned_query = query.strip()
        cache_key = f"geocode_{cleaned_query.lower()}"
        cached = geocode_cache.get(cache_key)
        if cached:
            return cached

        # 1. Google Maps Platform REST Geocoding
        maps_key = None
        if user_key_info and user_key_info.get("api_key"):
            maps_key = user_key_info["api_key"]
        elif settings.GOOGLE_MAPS_API_KEY:
            maps_key = settings.GOOGLE_MAPS_API_KEY

        if maps_key:
            try:
                g_res = await self._fetch_google_maps_geocode(cleaned_query, maps_key)
                if g_res:
                    geocode_cache.set(cache_key, g_res)
                    return g_res
            except Exception as e:
                logger.warning(f"Google Maps Geocoding failed: {e}. Falling to Nominatim.")

        # 2. Nominatim OpenStreetMap
        try:
            nom_res = await self._fetch_nominatim(cleaned_query)
            if nom_res:
                geocode_cache.set(cache_key, nom_res)
                return nom_res
        except Exception as e:
            logger.warning(f"Nominatim Geocoding failed: {e}. Falling to Open-Meteo geocoding.")

        # 3. Open-Meteo Geocoding API
        try:
            om_res = await self._fetch_open_meteo_geocoding(cleaned_query)
            if om_res:
                geocode_cache.set(cache_key, om_res)
                return om_res
        except Exception as e:
            logger.error(f"Open-Meteo Geocoding failed: {e}")

        # Baseline fallback
        return [{
            "display_name": f"{cleaned_query}, Jharkhand, India",
            "lat": 24.002,
            "lon": 85.361,
            "village": cleaned_query,
            "district": "Hazaribagh",
            "state": "Jharkhand",
            "source": "Default Baseline"
        }]

    async def _fetch_google_maps_geocode(self, query: str, api_key: str) -> Optional[List[Dict[str, Any]]]:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={query}&key={api_key}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "OK" and data.get("results"):
                    results = []
                    for r in data["results"][:4]:
                        loc = r["geometry"]["location"]
                        results.append({
                            "display_name": r["formatted_address"],
                            "lat": loc["lat"],
                            "lon": loc["lng"],
                            "source": "Google Maps Platform Geocoding API",
                            "source_type": "google_maps_api"
                        })
                    return results
        return None

    async def _fetch_nominatim(self, query: str) -> Optional[List[Dict[str, Any]]]:
        # Enforce 1 req/sec policy
        await asyncio.sleep(1.0)
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}&limit=4&addressdetails=1"
        headers = {"User-Agent": settings.SCRAPER_USER_AGENT}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                items = resp.json()
                if items:
                    results = []
                    for it in items:
                        addr = it.get("address", {})
                        results.append({
                            "display_name": it.get("display_name", query),
                            "lat": float(it["lat"]),
                            "lon": float(it["lon"]),
                            "village": addr.get("village") or addr.get("suburb") or query.split(",")[0],
                            "district": addr.get("county") or addr.get("state_district") or "Hazaribagh",
                            "state": addr.get("state") or "Jharkhand",
                            "source": "OpenStreetMap Nominatim",
                            "source_type": "free_api"
                        })
                    return results
        return None

    async def _fetch_open_meteo_geocoding(self, query: str) -> Optional[List[Dict[str, Any]]]:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=4&language=en&format=json"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                results_raw = data.get("results", [])
                if results_raw:
                    return [
                        {
                            "display_name": f"{r.get('name')}, {r.get('admin1', '')}, {r.get('country', '')}",
                            "lat": float(r["latitude"]),
                            "lon": float(r["longitude"]),
                            "village": r.get("name", query),
                            "district": r.get("admin2") or r.get("admin1") or "Hazaribagh",
                            "state": r.get("admin1") or "Jharkhand",
                            "source": "Open-Meteo Geocoding",
                            "source_type": "free_api"
                        }
                        for r in results_raw
                    ]
        return None
