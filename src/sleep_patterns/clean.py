"""Turn raw tracker sessions into one row per night."""

import pandas as pd


def add_derived(sleep):
    out = sleep.copy()
    out["hours"] = (out["end"] - out["start"]).dt.total_seconds() / 3600
    out["night"] = out["start"].dt.normalize()
    out["weekday"] = out["night"].dt.day_name()
    return out
