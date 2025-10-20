"""Turn raw tracker sessions into one row per night."""

import pandas as pd


def add_derived(sleep):
    out = sleep.copy()
    out["hours"] = (out["end"] - out["start"]).dt.total_seconds() / 3600
    out["night"] = (out["start"] - pd.Timedelta(hours=12)).dt.normalize()
    out["weekday"] = out["night"].dt.day_name()
    return out


def nightly(sleep, min_hours=2.0, max_hours=14.0):
    """One row per night: naps and stuck sessions dropped, longest session kept."""
    df = add_derived(sleep)
    df = df[df["hours"].between(min_hours, max_hours)]
    df = df.sort_values("hours").drop_duplicates("night", keep="last")
    return df.sort_values("night").reset_index(drop=True)
