import pandas as pd

from sleep_patterns.io import load_caffeine, load_sleep


def test_load_sleep_parses_timestamps(tmp_path):
    p = tmp_path / "s.csv"
    p.write_text("start,end,awakenings,efficiency\n2025-01-01 23:00:00,2025-01-02 07:00:00,1,90.0\n")
    df = load_sleep(p)
    assert pd.api.types.is_datetime64_any_dtype(df["start"])
    assert (df["end"] - df["start"]).iloc[0] == pd.Timedelta(hours=8)


def test_load_caffeine_parses_timestamps(tmp_path):
    p = tmp_path / "c.csv"
    p.write_text("timestamp,drink,caffeine_mg\n2025-01-01 08:00:00,coffee,95\n")
    df = load_caffeine(p)
    assert df["timestamp"].dt.hour.iloc[0] == 8
