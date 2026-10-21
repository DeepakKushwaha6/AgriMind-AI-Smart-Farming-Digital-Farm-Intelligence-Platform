from app.services.decision_engine import DecisionEngine
from app.connectors.market_connector import MarketConnector


def test_irrigation_hold_on_heavy_rain():
    # 18.2mm rain forecasted tomorrow -> Should advise holding irrigation
    advice = DecisionEngine.evaluate_irrigation(
        crop="Paddy (Sahbhagi)",
        stage="Day 45 Active Tillering",
        soil_moisture_pct=26,
        rain_7d_mm=42.0,
        tomorrow_rain_mm=18.2
    )
    assert "Hold borewell irrigation" in advice["action"]
    assert "92%" in advice["confidence"]
    assert advice["status"] == "Active"


def test_fertilizer_split_urea_rain_delay():
    # Rain expected tomorrow -> Delay top dressing to avoid leaching loss
    advice = DecisionEngine.evaluate_fertilizer(
        crop="Paddy",
        stage="Day 45 Panicle Initiation",
        soil_n=218.0,
        soil_ph=6.1,
        soil_zn=0.52,
        heavy_rain_tomorrow=True
    )
    assert "Delay 2nd top-dressing" in advice["action"]
    assert "runoff and leaching loss" in advice["reason"]


def test_net_realisation_math():
    conn = MarketConnector()
    # 25 Qtl @ 2350, 12km local transport (0.9/km/qtl = 10.8) + 20 handling + 1% commission (23.5)
    res = conn.calculate_net_realisation(
        quantity_qtl=25.0,
        modal_price=2350.0,
        distance_km=12.0,
        transport_rate_per_km_qtl=0.9,
        handling_per_qtl=20.0,
        commission_pct=1.0
    )
    assert res["gross_revenue"] == 58750.0
    assert res["net_realisation"] < res["gross_revenue"]
    assert res["net_per_qtl"] > 2250.0
