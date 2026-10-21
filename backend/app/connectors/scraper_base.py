import asyncio
import json
import os
import time
import urllib.robotparser
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from app.connectors.base import BaseConnector
from app.core.config import settings
from app.core.logging import logger

# Global per-domain rate limiter tracker
_DOMAIN_LAST_REQUEST_TIME: Dict[str, float] = {}
_ROBOTS_CACHE: Dict[str, urllib.robotparser.RobotFileParser] = {}


class ScraperConnector(BaseConnector):
    """
    Polite, production-quality scraper base class with:
    1. robots.txt compliance checking
    2. Per-domain rate limits (e.g. 1 request every 3s)
    3. Descriptive User-Agent identification
    4. Conditional GET (ETag / If-None-Match and If-Modified-Since)
    5. HTML structural pattern validation (to reject broken or ad-heavy garbage pages)
    6. Circuit breaker & backoff retries
    """

    def __init__(
        self,
        category: str,
        name: str,
        rate_limit_seconds: float = 3.0,
        timeout: float = 10.0
    ):
        super().__init__(name=name, timeout=timeout, max_retries=3)
        self.category = category
        self.rate_limit_seconds = rate_limit_seconds
        self.user_agent = settings.SCRAPER_USER_AGENT
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        config_path = os.path.join(os.path.dirname(__file__), "scraper_config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load scraper_config.json: {e}")
        return {}

    async def _enforce_rate_limit(self, domain: str):
        """Enforces at most one request every N seconds per domain."""
        now = time.time()
        last_req = _DOMAIN_LAST_REQUEST_TIME.get(domain, 0.0)
        elapsed = now - last_req
        if elapsed < self.rate_limit_seconds:
            wait_time = self.rate_limit_seconds - elapsed
            logger.info(f"[{self.name}] Rate limiting domain {domain}: pausing {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        _DOMAIN_LAST_REQUEST_TIME[domain] = time.time()

    async def is_allowed_by_robots(self, target_url: str) -> bool:
        """Checks if scraping the given URL is permitted by the site's robots.txt."""
        parsed = urlparse(target_url)
        domain = parsed.netloc
        robots_url = f"{parsed.scheme}://{domain}/robots.txt"

        if domain not in _ROBOTS_CACHE:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(robots_url, headers={"User-Agent": self.user_agent})
                    if resp.status_code == 200:
                        rp.parse(resp.text.splitlines())
                    else:
                        rp.allow_all = True
            except Exception:
                # If robots.txt cannot be fetched, default to polite allowed
                rp.allow_all = True
            _ROBOTS_CACHE[domain] = rp

        rp = _ROBOTS_CACHE[domain]
        allowed = rp.can_fetch(self.user_agent, target_url)
        if not allowed:
            logger.warning(f"[{self.name}] Scraping forbidden by robots.txt for: {target_url}")
        return allowed

    async def fetch_page(
        self,
        url: str,
        etag: Optional[str] = None,
        last_modified: Optional[str] = None
    ) -> Tuple[Optional[str], int, Optional[str], Optional[str]]:
        """
        Executes a polite conditional GET request.
        Returns: (html_text, status_code, new_etag, new_last_modified)
        """
        domain = urlparse(url).netloc
        if not await self.is_allowed_by_robots(url):
            raise PermissionError(f"Scraping blocked by robots.txt for {url}")

        await self._enforce_rate_limit(domain)

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        }
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            new_etag = response.headers.get("ETag")
            new_last_modified = response.headers.get("Last-Modified")

            if response.status_code == 304:
                logger.info(f"[{self.name}] 304 Not Modified for {url}")
                return None, 304, new_etag or etag, new_last_modified or last_modified

            response.raise_for_status()
            return response.text, response.status_code, new_etag, new_last_modified

    def validate_html_structure(self, soup: BeautifulSoup, expected_selectors: List[str]) -> bool:
        """
        Validates that expected semantic HTML tags or classes exist.
        If the page layout changed or anti-bot CAPTCHA was triggered, marks as invalid.
        """
        for selector in expected_selectors:
            if not soup.select(selector):
                logger.warning(
                    f"[{self.name}] HTML structural validation failed: selector '{selector}' missing"
                )
                return False
        return True
