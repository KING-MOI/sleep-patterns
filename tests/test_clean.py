import pandas as pd

from sleep_patterns.clean import add_derived


def _sessions(*pairs):
    return pd.DataFrame(
        {
            "start": pd.to_datetime([a for a, _ in pairs]),
            "end": pd.to_datetime([b for _, b in pairs]),
        }
    )


def test_hours_across_midnight():
    df = add_derived(_sessions(("2025-03-07 23:30", "2025-03-08 07:00")))
    assert df["hours"].iloc[0] == 7.5


def test_after_midnight_bedtime_belongs_to_previous_night():
    # 00:40 on Saturday is still Friday night
    df = add_derived(_sessions(("2025-03-08 00:40", "2025-03-08 09:10")))
    assert df["night"].iloc[0] == pd.Timestamp("2025-03-07")
    assert df["weekday"].iloc[0] == "Friday"
