import pandas as pd

from sleep_patterns.metrics import WEEKDAYS, weekday_summary, worst_weekday


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
