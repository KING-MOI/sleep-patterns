import pandas as pd

from sleep_patterns.caffeine import daily_caffeine


def _log(*rows):
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime([t for t, _ in rows]),
            "drink": "coffee",
            "caffeine_mg": [mg for _, mg in rows],
        }
    )


def test_daily_caffeine_splits_late_intake():
    log = _log(("2025-02-03 08:00", 95), ("2025-02-03 15:30", 63), ("2025-02-04 09:00", 47))
    out = daily_caffeine(log)
    assert out.loc["2025-02-03", "total_mg"] == 158
    assert out.loc["2025-02-03", "late_mg"] == 63
    assert out.loc["2025-02-03", "last_drink"] == 15.5
    assert out.loc["2025-02-04", "late_mg"] == 0
