import pandas as pd

from sleep_patterns.metrics import (
    WEEKDAYS,
    bedtime_spread,
    sleep_debt,
    social_jetlag,
    weekday_summary,
    worst_weekday,
)


def _nights(hours, start="2025-01-06"):
    night = pd.date_range(start, periods=len(hours), freq="D")
    return pd.DataFrame(
        {
            "night": night,
            "weekday": night.day_name(),
            "hours": hours,
            "efficiency": 90.0,
            "awakenings": 1,
        }
    )


def test_weekday_summary_is_monday_first():
    out = weekday_summary(_nights([7.0] * 14))
    assert list(out.index) == WEEKDAYS
    assert (out["nights"] == 2).all()


def test_worst_weekday_picks_lowest_mean():
    hours = [7, 7, 7, 7, 7, 7, 5] * 2
    assert worst_weekday(_nights(hours)) == "Sunday"


def test_sleep_debt_rolling_window():
    debt = sleep_debt(_nights([6.5] * 14), target=7.5, window=7)
    assert debt["deficit"].eq(1.0).all()
    assert debt["debt"].iloc[-1] == 7.0
    assert debt["cumulative"].iloc[-1] == 14.0


def test_sleep_debt_gap_does_not_count_as_rest():
    n = _nights([6.5] * 14).drop(index=[5, 6])
    debt = sleep_debt(n, target=7.5, window=7)
    assert len(debt) == 14
    assert debt["deficit"].isna().sum() == 2
    assert debt["debt"].iloc[7] == 7.0


def test_social_jetlag_is_weekend_minus_weekday_midsleep():
    n = _nights([7.0] * 7)
    n["midsleep"] = [27.0, 27.0, 27.0, 27.0, 29.0, 29.5, 27.0]
    assert social_jetlag(n) == 29.25 - 27.0


def test_bedtime_spread_in_minutes():
    n = _nights([7.0] * 14)
    n["bedtime"] = [23.0] * 7 + [24.0] * 7
    spread = bedtime_spread(n)
    assert list(spread.index) == WEEKDAYS
    assert round(spread["Monday"], 1) == round(60 * 0.7071, 1)
