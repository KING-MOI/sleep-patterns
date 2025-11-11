import pandas as pd

from sleep_patterns.caffeine import (
    by_last_drink,
    caffeine_correlations,
    daily_caffeine,
    late_caffeine_effect,
    with_caffeine,
)


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


def test_by_last_drink_buckets_and_no_caffeine_days():
    nights = _nights(["2025-02-03", "2025-02-04", "2025-02-05"], [5.0, 7.0, 8.0])
    log = _log(("2025-02-03 17:00", 95), ("2025-02-04 09:00", 95))
    out = by_last_drink(with_caffeine(nights, log))
    assert list(out.index) == ["none", "00-12h", "12-14h", "14-16h", "16-24h"]
    assert out.loc["none", "mean_hours"] == 8.0
    assert out.loc["00-12h", "mean_hours"] == 7.0
    assert out.loc["16-24h", "mean_hours"] == 5.0
    assert out.loc["12-14h", "nights"] == 0


def test_late_caffeine_effect_removes_month_confound():
    import numpy as np

    rng = np.random.default_rng(0)
    night = pd.date_range("2025-01-01", periods=365, freq="D")
    busy = night.month.isin([3, 4, 11])
    late_mg = rng.uniform(0, 100, 365) + busy * 150
    hours = 7.5 - 0.004 * late_mg - busy * 0.8 + rng.normal(0, 0.1, 365)
    merged = pd.DataFrame({"night": night, "late_mg": late_mg, "hours": hours})

    raw = np.polyfit(late_mg, hours, 1)[0]
    assert raw < -0.006
    assert abs(late_caffeine_effect(merged) - -0.004) < 0.0005
