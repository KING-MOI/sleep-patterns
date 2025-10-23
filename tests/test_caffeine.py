import pandas as pd

from sleep_patterns.caffeine import caffeine_correlations, daily_caffeine, with_caffeine


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


def _nights(days, hours):
    night = pd.to_datetime(days)
    return pd.DataFrame(
        {"night": night, "hours": hours, "efficiency": 90.0, "awakenings": [1, 2, 3][: len(days)]}
    )


def test_with_caffeine_fills_days_without_a_log():
    nights = _nights(["2025-02-03", "2025-02-04"], [6.0, 8.0])
    out = with_caffeine(nights, _log(("2025-02-03 16:00", 95)))
    assert list(out["late_mg"]) == [95, 0]
    assert list(out["drinks"]) == [1, 0]


def test_correlation_sign():
    nights = _nights(["2025-02-03", "2025-02-04", "2025-02-05"], [5.0, 6.0, 8.0])
    log = _log(("2025-02-03 16:00", 200), ("2025-02-04 16:00", 100), ("2025-02-05 09:00", 50))
    corr = caffeine_correlations(with_caffeine(nights, log))
    assert corr.loc[("pearson", "late_mg"), "hours"] < -0.9
    assert corr.loc[("spearman", "total_mg"), "hours"] == -1.0
