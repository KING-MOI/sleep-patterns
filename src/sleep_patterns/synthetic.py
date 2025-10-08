"""Generate a synthetic year of sleep-tracker data.

The real export is private, so this produces a stand-in with the same
columns and roughly the same quirks.
"""

import numpy as np
import pandas as pd


def generate_sleep(start="2025-01-01", days=365, seed=7):
    rng = np.random.default_rng(seed)
    nights = pd.date_range(start, periods=days, freq="D")

    bed_hour = rng.normal(23.3, 0.6, days)
    duration = rng.normal(7.2, 0.7, days)

    start_ts = nights + pd.to_timedelta(bed_hour, unit="h")
    end_ts = start_ts + pd.to_timedelta(duration, unit="h")

    return pd.DataFrame(
        {
            "start": start_ts.round("min"),
            "end": end_ts.round("min"),
        }
    )
