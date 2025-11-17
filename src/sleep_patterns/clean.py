"""Turn raw tracker sessions into one row per night."""

import pandas as pd


def add_derived(sleep):
    out = sleep.copy()
    out["hours"] = (out["end"] - out["start"]).dt.total_seconds() / 3600
    out["night"] = (out["start"] - pd.Timedelta(hours=12)).dt.normalize()
    out["weekday"] = out["night"].dt.day_name()
    # clock hours measured from the evening's midnight, so 00:30 is 24.5, not 0.5
    out["bedtime"] = (out["start"] - out["night"]).dt.total_seconds() / 3600
    out["waketime"] = (out["end"] - out["night"]).dt.total_seconds() / 3600
    out["midsleep"] = (out["bedtime"] + out["waketime"]) / 2
    return out


def nightly(sleep, min_hours=2.0, max_hours=14.0):
    """One row per night: naps and stuck sessions dropped, longest session kept."""
    df = add_derived(sleep)
    df = df[df["hours"].between(min_hours, max_hours)]
    df = df.sort_values("hours").drop_duplicates("night", keep="last")
    return df.sort_values("night").reset_index(drop=True)
