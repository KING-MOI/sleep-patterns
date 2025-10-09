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


DRINKS = {
    "coffee": 95,
    "espresso": 63,
    "black tea": 47,
    "cola": 34,
    "energy drink": 160,
}
DRINK_WEIGHTS = [0.45, 0.2, 0.2, 0.08, 0.07]


def generate_caffeine(start="2025-01-01", days=365, seed=7):
    rng = np.random.default_rng(seed + 1)
    days_idx = pd.date_range(start, periods=days, freq="D")
    crunch = _seasonal_loss(days_idx) > 0

    rows = []
    for day, in_crunch in zip(days_idx, crunch):
        n = rng.poisson(2.6 if in_crunch else 1.8)
        # first drink in the morning, the rest spread over the day
        hours = np.sort(np.concatenate([
            rng.normal(8.0, 0.6, min(n, 1)),
            rng.uniform(10, 19.5 if in_crunch else 17.5, max(n - 1, 0)),
        ]))
        for h in hours:
            drink = rng.choice(list(DRINKS), p=DRINK_WEIGHTS)
            rows.append((day + pd.Timedelta(hours=float(h)), drink, DRINKS[drink]))

    out = pd.DataFrame(rows, columns=["timestamp", "drink", "caffeine_mg"])
    out["timestamp"] = out["timestamp"].dt.round("min")
    return out


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
