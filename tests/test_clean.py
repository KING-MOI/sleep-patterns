import pandas as pd

from sleep_patterns.clean import add_derived, nightly


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


def test_nightly_drops_naps_and_stuck_sessions():
    raw = _sessions(
        ("2025-03-07 23:30", "2025-03-08 07:00"),
        ("2025-03-08 14:00", "2025-03-08 14:30"),
        ("2025-03-09 13:00", "2025-03-10 05:00"),
    )
    out = nightly(raw)
    assert list(out["night"]) == [pd.Timestamp("2025-03-07")]


def test_bedtime_does_not_wrap_at_midnight():
    df = add_derived(
        _sessions(
            ("2025-03-07 23:30", "2025-03-08 07:00"),
            ("2025-03-09 00:30", "2025-03-09 08:00"),
        )
    )
    assert list(df["bedtime"]) == [23.5, 24.5]
    assert list(df["waketime"]) == [31.0, 32.0]
    assert df["bedtime"].mean() == 24.0
