"""Read the tracker exports into typed DataFrames."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def load_sleep(path=DATA_DIR / "sleep_log.csv"):
    return pd.read_csv(path, parse_dates=["start", "end"])


def load_caffeine(path=DATA_DIR / "caffeine_log.csv"):
    return pd.read_csv(path, parse_dates=["timestamp"])
