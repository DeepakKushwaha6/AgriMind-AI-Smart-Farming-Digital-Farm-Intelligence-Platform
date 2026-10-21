import pytest
from bs4 import BeautifulSoup
from app.connectors.scraper_base import ScraperConnector
from app.connectors.market_scraper import MarketScraperConnector


def test_scraper_structure_validation_success():
    scraper = ScraperConnector(category="mandi", name="TestScraper")
    valid_html = """
    <html>
      <body>
        <div class="mandi-price-table">
          <table>
            <thead><tr><th>Market</th><th>Arrivals</th><th>Modal Price</th></tr></thead>
            <tbody><tr><td>Hazaribagh</td><td>100</td><td>₹ 2,350</td></tr></tbody>
          </table>
        </div>
      </body>
    </html>
    """
    soup = BeautifulSoup(valid_html, "html.parser")
    assert scraper.validate_html_structure(soup, [".mandi-price-table", "table"]) is True


def test_scraper_structure_validation_failure_on_layout_change():
    scraper = ScraperConnector(category="mandi", name="TestScraper")
    broken_html = """
    <html>
      <body>
        <div class="ad-banner">Advertisement</div>
        <p>Site under maintenance or layout altered.</p>
      </body>
    </html>
    """
    soup = BeautifulSoup(broken_html, "html.parser")
    # Expect failure because expected table selector is missing
    assert scraper.validate_html_structure(soup, [".mandi-price-table"]) is False


def test_market_commodity_alias_normalization():
    mandi_scraper = MarketScraperConnector()
    assert mandi_scraper.normalize_commodity_name("dhan") == "Paddy (Common)"
    assert mandi_scraper.normalize_commodity_name("rice paddy") == "Paddy (Common)"
    assert mandi_scraper.normalize_commodity_name("gehun") == "Wheat"
    assert mandi_scraper.normalize_commodity_name("makka") == "Maize"
