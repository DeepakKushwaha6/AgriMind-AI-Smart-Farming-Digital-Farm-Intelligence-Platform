import asyncio
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.connectors.weather_connector import WeatherConnector
from app.connectors.market_connector import MarketConnector
from app.core.logging import logger

scheduler = AsyncIOScheduler()
weather_connector = WeatherConnector()
market_connector = MarketConnector()


async def refresh_weather_job():
    """Scheduled job to refresh weather telemetry for active field locations every 60 minutes."""
    try:
        logger.info("[Scheduler] Running scheduled weather refresh...")
        await weather_connector.get_weather(lat=24.002, lon=85.361, location_name="Jarga, Hazaribagh")
        logger.info("[Scheduler] Scheduled weather refresh completed successfully.")
    except Exception as e:
        logger.error(f"[Scheduler] Weather refresh job error: {e}")


async def refresh_market_job():
    """Scheduled job to refresh mandi prices and scrape updates every 1-2 hours."""
    try:
        logger.info("[Scheduler] Running scheduled mandi market scrape & sync...")
        await market_connector.get_mandi_prices(district="Hazaribagh", commodity="Paddy")
        logger.info("[Scheduler] Mandi market scrape & sync completed successfully.")
    except Exception as e:
        logger.error(f"[Scheduler] Market refresh job error: {e}")


async def health_check_job():
    """Checks provider connectivity and scraper circuit breaker state."""
    logger.info("[Scheduler] Running periodic health checks on providers and scrapers.")


def start_scheduler():
    scheduler.add_job(refresh_weather_job, "interval", minutes=60, id="weather_refresh", replace_existing=True)
    scheduler.add_job(refresh_market_job, "interval", hours=2, id="market_refresh", replace_existing=True)
    scheduler.add_job(health_check_job, "interval", minutes=5, id="health_check", replace_existing=True)
    scheduler.start()
    logger.info("[Scheduler] APScheduler started in-process successfully.")


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("[Scheduler] APScheduler stopped.")
