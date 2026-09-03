from datetime import date

from models.site import Site
from power_engine.analysis.battery_analysis import BatteryAnalysis


def test_battery_analysis_returns_score_and_reasons():
    site = Site({
        "siteid": "SBY001",
        "battery": "VRLA",
        "total_bank": 1,
        "total_load_rectifier_a": 20,
        "tgl_instalasi_battery": date(2020, 1, 1),
        "status_warranty_battery": "Out of Warranty",
    })

    result = BatteryAnalysis.analyze(site)

    assert result.health_score == 30
    assert result.is_critical
    assert result.health_reasons
    assert result.status == "CRITICAL"
