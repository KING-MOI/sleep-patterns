"""Generate a synthetic year of sleep-tracker data.

The real export is private, so this produces a stand-in with the same
columns and roughly the same quirks.
"""

import numpy as np
import pandas as pd

# hours added to bedtime / duration, indexed by weekday of the night (Mon=0)
BEDTIME_SHIFT = np.array([0.0, 0.0, 0.1, 0.3, 1.1, 1.3, 0.6])
DURATION_SHIFT = np.array([0.0, 0.1, -0.1, -0.3, 0.5, 0.9, -0.8])

# (first day, last day, hours lost per night) - exam season and end-of-year deadlines
CRUNCH_PERIODS = [
    ("03-10", "04-25", 0.7),
    ("11-03", "12-12", 0.5),
]
SUMMER = ("07-01", "08-20", -0.3)


def _seasonal_loss(nights):
    loss = np.zeros(len(nights))
    md = nights.strftime("%m-%d")
    for lo, hi, hours in CRUNCH_PERIODS + [SUMMER]:
        loss[(md >= lo) & (md <= hi)] += hours
    return loss


def generate_sleep(start="2025-01-01", days=365, seed=7):
    rng = np.random.default_rng(seed)
    nights = pd.date_range(start, periods=days, freq="D")

    weekday = nights.weekday.to_numpy()

    bed_hour = rng.normal(23.1, 0.5, days) + BEDTIME_SHIFT[weekday]
    duration = (
        rng.normal(7.2, 0.6, days) + DURATION_SHIFT[weekday] - _seasonal_loss(nights)
    )

    start_ts = nights + pd.to_timedelta(bed_hour, unit="h")
    end_ts = start_ts + pd.to_timedelta(duration, unit="h")

    return pd.DataFrame(
        {
            "start": start_ts.round("min"),
            "end": end_ts.round("min"),
        }
    )
