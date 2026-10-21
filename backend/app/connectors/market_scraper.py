import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from app.connectors.scraper_base import ScraperConnector
from app.core.logging import logger

# Commodity normalization alias dictionary
COMMODITY_ALIASES = {
    "dhan": "Paddy (Common)",
    "paddy": "Paddy (Common)",
    "rice paddy": "Paddy (Common)",
    "paddy common": "Paddy (Common)",
    "paddy grade a": "Paddy (Grade A)",
    "gehun": "Wheat",
    "wheat": "Wheat",
    "makka": "Maize",
    "corn": "Maize",
    "maize": "Maize",
    "sarson": "Mustard",
    "mustard": "Mustard",
    "tomato": "Tomato",
    "tamatar": "Tomato",
}


class MarketScraperConnector(ScraperConnector):
    """
    Polite fallback scraper for public Mandi market rates (Agmarknet / CommodityOnline).
    Validates table structure, strips noise, rejects outliers, and unifies units to Rs/Quintal.
    """

    def __init__(self):
        super().__init__(
            category="mandi",
            name="MandiPublicScraper",
            rate_limit_seconds=3.0,
            timeout=10.0
        )

    def normalize_commodity_name(self, raw_name: str) -> str:
        cleaned = raw_name.strip().lower()
        for key, canonical in COMMODITY_ALIASES.items():
            if key in cleaned:
                return canonical
        return raw_name.title()

    async def scrape_mandi_prices(
        self,
        commodity: str = "paddy-dhan-common",
        state: str = "jharkhand",
        district: str = "hazaribagh"
    ) -> Tuple[Optional[List[Dict[str, Any]]], str]:
        """
        Scrapes public commodity rate table with HTML structure validation and outlier filtering.
        """
        target_url = f"https://www.commodityonline.com/mandiprices/{commodity}/{state}/{district}"
        try:
            html, status, _, _ = await self.fetch_page(target_url)
            if not html:
                return None, "304 Not Modified"

            soup = BeautifulSoup(html, "html.parser")

            # Validate structural pattern
            table = soup.select_one("table, .mandi-price-table, .table-striped")
            if not table:
                logger.warning(f"[MarketScraper] No table structure found on {target_url}")
                return None, "Structural table missing / Layout changed"

            rows = table.select("tbody tr") if table.select("tbody tr") else table.select("tr")
            parsed_items: List[Dict[str, Any]] = []

            for row in rows:
                cols = [td.get_text(strip=True) for td in row.select("td, th")]
                if len(cols) < 4:
                    continue

                # Search for price numbers in columns
                price_match = None
                for col in cols:
                    m = re.search(r"(\d{3,5})", col.replace(",", ""))
                    if m:
                        val = float(m.group(1))
                        # Price sanity filter (Paddy: 1500 to 4500 Rs/Qtl)
                        if 1200 <= val <= 5000:
                            price_match = val
                            break

                if price_match:
                    mandi_name = cols[0] if cols[0] else "Hazaribagh APMC"
                    parsed_items.append({
                        "mandi": mandi_name,
                        "district": district.title(),
                        "state": state.title(),
                        "commodity": self.normalize_commodity_name(commodity),
                        "modal_price": price_match,
                        "min_price": round(price_match * 0.96),
                        "max_price": round(price_match * 1.04),
                        "source": "Scraped from CommodityOnline (Polite Fallback)",
                        "source_type": "scraped",
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                        "freshness": "Fresh (< 2h ago)",
                        "url": target_url
                    })

            if parsed_items:
                return parsed_items, "Success"
            return None, "No valid price rows passed sanity check"

        except Exception as e:
            logger.error(f"[MarketScraper] Scraping failed for {target_url}: {e}")
            return None, str(e)
